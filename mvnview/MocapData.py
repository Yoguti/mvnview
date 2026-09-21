from pathlib import Path

import numpy as np


class MocapData:
	def __init__(self, file_path):
		if not Path(file_path).exists():
			raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

		self.data = np.load(file_path)
		self.position = self._get("position")
		self.orientation = self._get("orientation")
		self.time = self._get("time")
		self.segment_names = self._get("segment_names")
		self.jointAngle = self._get("jointAngle")
		self.jointAngleXZY = self._get("jointAngleXZY")
		self.jointAngleErgo = self._get("jointAngleErgo")
		self.jointAngleErgoXZY = self._get("jointAngleErgoXZY")
		self.joint_names = self._get("joint_names")
		self.velocity = self._get("velocity")
		self.acceleration = self._get("acceleration")
		self.angularVelocity = self._get("angularVelocity")
		self.angularAcceleration = self._get("angularAcceleration")
		self.footContacts = self._get("footContacts")
		self.sensorFreeAcceleration = self._get("sensorFreeAcceleration")
		self.sensorMagneticField = self._get("sensorMagneticField")
		self.sensorOrientation = self._get("sensorOrientation")
		self.centerOfMass = self._get("centerOfMass")

	def _get(self, name):
		return self.data[name] if name in self.data else None

	def get_position(self):
		self.position = self._get("position")
		return self.position

	def get_orientation(self):
		self.orientation = self._get("orientation")
		return self.orientation

	def get_time(self):
		self.time = self._get("time")
		return self.time

	def get_segment_names(self):
		self.segment_names = self._get("segment_names")
		return self.segment_names

	def get_jointAngle(self):
		self.jointAngle = self._get("jointAngle")
		return self.jointAngle

	def get_jointAngleXZY(self):
		self.jointAngleXZY = self._get("jointAngleXZY")
		return self.jointAngleXZY

	def get_jointAngleErgo(self):
		self.jointAngleErgo = self._get("jointAngleErgo")
		return self.jointAngleErgo

	def get_jointAngleErgoXZY(self):
		self.jointAngleErgoXZY = self._get("jointAngleErgoXZY")
		return self.jointAngleErgoXZY

	def get_joint_names(self):
		self.joint_names = self._get("joint_names")
		return self.joint_names

	def get_velocity(self):
		self.velocity = self._get("velocity")
		return self.velocity

	def get_acceleration(self):
		self.acceleration = self._get("acceleration")
		return self.acceleration

	def get_angularVelocity(self):
		self.angularVelocity = self._get("angularVelocity")
		return self.angularVelocity

	def get_angularAcceleration(self):
		self.angularAcceleration = self._get("angularAcceleration")
		return self.angularAcceleration

	def get_footContacts(self):
		self.footContacts = self._get("footContacts")
		return self.footContacts

	def get_sensorFreeAcceleration(self):
		self.sensorFreeAcceleration = self._get("sensorFreeAcceleration")
		return self.sensorFreeAcceleration

	def get_sensorMagneticField(self):
		self.sensorMagneticField = self._get("sensorMagneticField")
		return self.sensorMagneticField

	def get_sensorOrientation(self):
		self.sensorOrientation = self._get("sensorOrientation")
		return self.sensorOrientation

	def get_centerOfMass(self):
		self.centerOfMass = self._get("centerOfMass")
		return self.centerOfMass

	def _segment_index(self, name):
		if self.segment_names is None or name not in self.segment_names:
			raise ValueError(f"Segmento '{name}' não encontrado.")
		return np.where(self.segment_names == name)[0][0]

	def get_full_segment_data(self, name):
		index = self._segment_index(name)
		position_start = index * 3
		orientation_start = index * 4
		return (
			self.position[:, position_start:position_start + 3],
			self.orientation[:, orientation_start:orientation_start + 4],
			self.velocity[:, position_start:position_start + 3],
			self.acceleration[:, position_start:position_start + 3],
			self.angularVelocity[:, position_start:position_start + 3],
			self.angularAcceleration[:, position_start:position_start + 3],
		)

	def get_segment_position(self, name):
		index = self._segment_index(name)
		start = index * 3
		return self.position[:, start:start + 3]

	def get_segment_orientation(self, name):
		index = self._segment_index(name)
		start = index * 4
		return self.orientation[:, start:start + 4]

	def get_segment_velocity(self, name):
		index = self._segment_index(name)
		start = index * 3
		return self.velocity[:, start:start + 3]

	def get_segment_acceleration(self, name):
		index = self._segment_index(name)
		start = index * 3
		return self.acceleration[:, start:start + 3]

	def get_segment_angular_velocity(self, name):
		index = self._segment_index(name)
		start = index * 3
		return self.angularVelocity[:, start:start + 3]

	def get_segment_angular_acceleration(self, name):
		index = self._segment_index(name)
		start = index * 3
		return self.angularAcceleration[:, start:start + 3]

	def get_distance(self, first_name, second_name):
		first_position = self.get_segment_position(first_name)
		second_position = self.get_segment_position(second_name)
		return np.linalg.norm(first_position - second_position, axis=1)

	# Compatibility wrappers; the implementations live in tools.py.
	def print_segment_names(self):
		from .tools import print_segment_names
		return print_segment_names(self)

	def print_joint_names(self):
		from .tools import print_joint_names
		return print_joint_names(self)

	def print_all_shapes(self):
		from .tools import print_all_shapes
		return print_all_shapes(self)


__all__ = ["MocapData"]
