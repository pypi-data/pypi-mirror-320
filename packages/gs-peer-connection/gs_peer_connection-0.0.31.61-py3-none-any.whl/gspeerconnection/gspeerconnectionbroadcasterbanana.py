import ast
import json
import logging
from threading import Thread
from time import sleep
import socketio
from aiortc import RTCPeerConnection, RTCRtpSender, RTCConfiguration, RTCIceServer, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay

try:
    import picamera
except:
    log = logging.getLogger(__name__)
    log.error("failed to import picamera")

from gspeerconnection.pitrack import PiH264Relay, PiH264CameraOutput

video_trackList = list()
pcs = set()
relay = None
microfon = None


class BroadcastThread(Thread):
    def __init__(self, cameraoutput):
        super(BroadcastThread, self).__init__()
        self.cameraoutput = cameraoutput

    def run(self):
        while True:
            buf = self.cameraoutput.nal_queue.get()
            if buf:
                for track in video_trackList:
                    track.write(buf)


class GSPeerConnectionBroadcasterPi:

    def getPiH264Relay(self):
        video_track = PiH264Relay(30)
        video_trackList.append(video_track)
        return video_track

    def getMicrofonRelay(self):
        global relay, microfon
        if relay is None:
            microfon = MediaPlayer("hw:1", format="alsa", options={
                "channels": "1",
                "sample_rate": "44100"
            })
            relay = MediaRelay()
        return relay.subscribe(microfon.audio)

    @classmethod
    async def create(cls, gsdbs, camera, oncommand=None):
        self = GSPeerConnectionBroadcasterPi()
        self.rtconfiList = []

        self.gsdbs = gsdbs
        self.oncommand = oncommand
        # picam.append(camera)
        if self.gsdbs.credentials["stunenable"]:
            self.rtconfiList.append(RTCIceServer(self.gsdbs.credentials["stunserver"]))
        if self.gsdbs.credentials["turnenable"]:
            for turnserver in self.gsdbs.credentials["turnserver"]:
                self.rtconfiList.append(RTCIceServer(urls=turnserver,
                                                     username=self.gsdbs.credentials["turnuser"],
                                                     credential=self.gsdbs.credentials["turnpw"]
                                                     ))

        camera.resolution = (self.gsdbs.credentials["hres"], self.gsdbs.credentials["vres"])
        camera.framerate = self.gsdbs.credentials["framerate"]
        sleep(1)  # camera warm-up time
        target_bitrate = camera.resolution[0] * \
                         camera.resolution[1] * \
                         camera.framerate * 0.150

        cameraOutput = PiH264CameraOutput()
        broadcast_thread = BroadcastThread(cameraOutput)
        camera.start_recording(
            cameraOutput,
            format="h264",
            profile="constrained",
            bitrate=int(target_bitrate),
            inline_headers=True,
            sei=False,
        )

        broadcast_thread.start()
        self.sio = socketio.AsyncClient()
        self.peerConnections = {}
        self._logger = logging.getLogger(__name__)
        self.webcam = None
        self.relay = None

        @self.sio.event
        async def connect():
            self._logger.info('connection established')

        @self.sio.event
        async def watcher(id, description):
            if type(description) == str:
                description = ast.literal_eval(description)
            desc = type('new_dict', (object,), description)

            offer = RTCSessionDescription(sdp=description["sdp"], type=description["type"])

            self._logger.debug(str(self.rtconfiList))

            if len(self.rtconfiList) > 0:
                pc = RTCPeerConnection(configuration=RTCConfiguration(self.rtconfiList))
            else:
                pc = RTCPeerConnection()

            self.peerConnections[id] = pc

            video = self.getPiH264Relay()
            audio = None

            @pc.on("connectionstatechange")
            async def on_connectionstatechange():
                print("Connection state is %s" % pc.connectionState)
                if pc.connectionState == "failed":
                    await pc.close()
                    self.peerConnections.pop(id, None)

            transceiver = pc.addTransceiver("video", direction="sendonly")

            capabilities = RTCRtpSender.getCapabilities("video")
            preferences = list(filter(lambda x: x.name == "H264", capabilities.codecs))
            preferences += list(filter(lambda x: x.name == "rtx", capabilities.codecs))
            transceiver.setCodecPreferences(preferences)

            if self.gsdbs.credentials["audio"]:
                pc.addTransceiver("audio", direction="sendonly")
                audio = self.getMicrofonRelay()
                pc.addTrack(audio)

            for t in pc.getTransceivers():
                if t.kind == "video":
                    pc.addTrack(video)

            await pc.setRemoteDescription(offer)

            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)

            await self.sio.emit("answer", {"id": id,
                                           "message": json.dumps(
                                               {"type": pc.localDescription.type,
                                                "sdp": pc.localDescription.sdp})})

        @self.sio.event
        async def command(commandcall):
            self.oncommand(self.gsdbs, commandcall)

        @self.sio.event
        async def joined(id):
            await self.sio.emit("broadcaster", id)

        @self.sio.event
        async def disconnectPeer(id):
            if id in self.peerConnections:
                await self.peerConnections[id].close()
                self.peerConnections.pop(id, None)

        @self.sio.event
        async def candidate(id, candidate):
            await self.peerConnections[id].addIceCandidate()

        @self.sio.event
        async def disconnect():
            self._logger.info('disconnected from server')

        connectURL = ""

        if "localhost" in self.gsdbs.credentials["signalserver"]:
            connectURL = f'{self.gsdbs.credentials["signalserver"]}:{str(self.gsdbs.credentials["signalport"])}'
        else:
            connectURL = self.gsdbs.credentials["signalserver"]

        await self.sio.connect(
            f'{connectURL}?gssession={self.gsdbs.cookiejar.get("session")}.{self.gsdbs.cookiejar.get("signature")}{self.gsdbs.credentials["cnode"]}')
        await self.sio.wait()
