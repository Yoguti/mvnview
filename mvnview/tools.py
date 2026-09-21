from pathlib import Path

import numpy as np

from .extraction import MVNX
from .MocapData import MocapData

def load(*args, **kwargs):
    return MVNX(*args, **kwargs)


def print_segment_names(data):
    print("Segmentos:")
    if data.segment_names is None:
        print("None")
        return

    column_count = 3
    row_count = (len(data.segment_names) + column_count - 1) // column_count
    columns = [
        data.segment_names[index * row_count:(index + 1) * row_count]
        for index in range(column_count)
    ]
    for row in range(row_count):
        print("  ".join(
            f"{str(column[row]):<{max(map(lambda name: len(str(name)), column), default=0)}}"
            for column in columns
            if row < len(column)
        ).rstrip())


def print_joint_names(data):
    print("Juntas:")
    for name in data.joint_names:
        print(name)


def print_all_shapes(data):
    def shape_or_none(value):
        return value.shape if value is not None else "None"

    print(f"posição: {shape_or_none(data.position)} --> (frames, (23 segmentos x 3 [x,y,z]))")
    print(f"orientação: {shape_or_none(data.orientation)} --> (frames, (23 segmentos x 4 [q0,q1,q2, q3]))")
    print(f"tempo: {shape_or_none(data.time)}")
    print(f"segmentos: {shape_or_none(data.segment_names)}")
    print(f"nomes das juntas: {shape_or_none(data.joint_names)}")
    print(f"ângulo das juntas: {shape_or_none(data.jointAngle)}\n")
    print(f"velocidade: {shape_or_none(data.velocity)} --> (frames, (23 segmentos x 3 [x,y,z]))")
    print(f"aceleração: {shape_or_none(data.acceleration)} --> (frames, (23 segmentos x 3 [x,y,z]))")
    print(f"velocidade angular: {shape_or_none(data.angularVelocity)} --> (frames, (23 segmentos x 3 [x,y,z]))")
    print(f"aceleração angular: {shape_or_none(data.angularAcceleration)} --> (frames, (23 segmentos x 3 [x,y,z]))")
    print(f"contatos dos pés: {shape_or_none(data.footContacts)} --> (frames, (23 segmentos x 3 [x,y,z]))")
    print(f"aceleração livre do sensor: {shape_or_none(data.sensorFreeAcceleration)} --> (frames, (23 segmentos x 3 [x,y,z]))")
    print(f"campo magnético do sensor: {shape_or_none(data.sensorMagneticField)} --> (frames, (23 segmentos x 3 [x,y,z]))")
    print(f"orientação do sensor: {shape_or_none(data.sensorOrientation)} --> (frames, (23 segmentos x 4 [q0,q1,q2, q3]))")
    print(f"centro de massa: {shape_or_none(data.centerOfMass)} --> (frames, (23 segmentos x 3 [x,y,z]))")


# LOAD AND SAVE FUNCTIONS

def save_mvnx_data(file_path, output_path):
    mocap = MVNX(file_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(
        output_path,
        jointAngle=mocap.jointAngle,
        jointAngleXZY=mocap.jointAngleXZY,
        jointAngleErgo=mocap.jointAngleErgo,
        jointAngleErgoXZY=mocap.jointAngleErgoXZY,
        position=mocap.position,
        orientation=mocap.orientation,
        velocity=mocap.velocity,
        acceleration=mocap.acceleration,
        angularVelocity=mocap.angularVelocity,
        angularAcceleration=mocap.angularAcceleration,
        footContacts=mocap.footContacts,
        sensorFreeAcceleration=mocap.sensorFreeAcceleration,
        sensorMagneticField=mocap.sensorMagneticField,
        sensorOrientation=mocap.sensorOrientation,
        centerOfMass=mocap.centerOfMass,
        time=list(map(int, mocap.time)), # conversão de string para int
        segment_names=list(mocap.segments.values()),
        joint_names=list(mocap.joints.keys()),
    )
    print(f"Dados e metadados salvos com sucesso em:\n{output_path.resolve()}")


__all__ = [
    "MocapData",
    "load",
    "save_mvnx_data",
    "print_segment_names",
    "print_joint_names",
    "print_all_shapes",
]

