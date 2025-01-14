import depthai as dai
from depthai_viewer._backend.device_configuration import (
    AiModelConfiguration,
    CameraConfiguration,
    CameraSensorResolution,
    PipelineConfiguration,
    StereoDepthConfiguration,
)

config = PipelineConfiguration(
    cameras=[
        CameraConfiguration(
            fps=15,
            resolution=CameraSensorResolution.THE_1080_P,
            kind=dai.CameraSensorType.COLOR,
            board_socket=dai.CameraBoardSocket.CAM_A,
            name="Color",
        ),
        CameraConfiguration(
            fps=15,
            resolution=CameraSensorResolution.THE_400_P,
            kind=dai.CameraSensorType.COLOR,
            board_socket=dai.CameraBoardSocket.CAM_B,
            stream_enabled=True,
            name="Left",
        ),
        CameraConfiguration(
            fps=15,
            resolution=CameraSensorResolution.THE_400_P,
            kind=dai.CameraSensorType.COLOR,
            board_socket=dai.CameraBoardSocket.CAM_C,
            stream_enabled=True,
            name="Right",
        ),
    ],
    stereo=StereoDepthConfiguration(
        align=dai.CameraBoardSocket.CAM_A,
        stereo_pair=(dai.CameraBoardSocket.CAM_B, dai.CameraBoardSocket.CAM_C),
        depth_preset=dai.node.StereoDepth.PresetMode.ROBOTICS,
    ),
    ai_model=AiModelConfiguration(camera=dai.CameraBoardSocket.CAM_A),
)
