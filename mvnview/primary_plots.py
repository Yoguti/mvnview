import numpy as np
import matplotlib.pyplot as plt


def plot_segment_position(data, segment_name):
	segment_position = np.asarray(data.get_segment_position(segment_name), dtype=float)
	if segment_position.ndim != 2 or segment_position.shape[1] != 3:
		raise ValueError("A posição do segmento deve ter o formato (frames, 3).")
	if not np.isfinite(segment_position).all():
		raise ValueError("A posição do segmento contém valores não finitos.")

	first_position = segment_position[0]
	last_position = segment_position[-1]
	fig = plt.figure(figsize=(10, 8))
	ax = fig.add_subplot(111, projection="3d")
	ax.plot(*segment_position.T, color="tab:blue", linewidth=1.5, label="trajetória do segmento")
	ax.scatter(*first_position, color="tab:green", s=50, label=f"início (altura z = {first_position[2]:.3f} m)")
	ax.scatter(*last_position, color="tab:red", s=50, label=f"fim (altura z = {last_position[2]:.3f} m)")
	ax.set_title(f"Movimento do {segment_name} através do espaço")
	ax.set_xlabel("X  (m)")
	ax.set_ylabel("Y  (m)")
	ax.set_zlabel("Z  (m)")
	ax.legend()

	data_min = segment_position.min(axis=0)
	data_max = segment_position.max(axis=0)
	margin = np.where(data_max - data_min > 0, (data_max - data_min) * 0.05, 0.05)
	ax.set_xlim3d(data_min[0] - margin[0], data_max[0] + margin[0])
	ax.set_ylim3d(data_min[1] - margin[1], data_max[1] + margin[1])
	ax.set_zlim3d(data_min[2] - margin[2], data_max[2] + margin[2])
	ax.set_box_aspect((1, 1, 1))
	plt.show()


def plot_flat_segment_position(data, segment_name):
	segment_position = np.asarray(data.get_segment_position(segment_name), dtype=float)
	if segment_position.ndim != 2 or segment_position.shape[1] != 3:
		raise ValueError("A posição do segmento deve ter o formato (frames, 3).")
	if not np.isfinite(segment_position).all():
		raise ValueError("A posição do segmento contém valores não finitos.")

	first_position = segment_position[0]
	last_position = segment_position[-1]
	fig = plt.figure(figsize=(10, 8))
	ax = fig.add_subplot(111, projection="3d")
	ax.plot(segment_position[:, 0], segment_position[:, 1], np.zeros(len(segment_position)), color="tab:blue", linewidth=1.5, label="trajetória do segmento (plano XY)")
	ax.scatter(first_position[0], first_position[1], 0, color="tab:green", s=50, label="início")
	ax.scatter(last_position[0], last_position[1], 0, color="tab:red", s=50, label="fim")
	ax.set_title(f"Movimento plano do {segment_name}")
	ax.set_xlabel("X  (m)")
	ax.set_ylabel("Y  (m)")
	ax.set_zlabel("")
	ax.set_zticks([])
	ax.legend()

	data_min = segment_position[:, :2].min(axis=0)
	data_max = segment_position[:, :2].max(axis=0)
	margin = np.where(data_max - data_min > 0, (data_max - data_min) * 0.05, 0.05)
	ax.set_xlim3d(data_min[0] - margin[0], data_max[0] + margin[0])
	ax.set_ylim3d(data_min[1] - margin[1], data_max[1] + margin[1])
	ax.set_zlim3d(-0.5, 0.5)
	ax.set_box_aspect((1, 1, 1))
	plt.show()


def _plot_scalar(data, segment_name, getter, title, ylabel):
	values = np.asarray(getter(segment_name), dtype=float)
	if values.ndim != 2 or values.shape[1] != 3:
		raise ValueError("Os dados do segmento devem ter o formato (frames, 3).")
	if not np.isfinite(values).all():
		raise ValueError("Os dados do segmento contêm valores não finitos.")
	plt.figure(figsize=(10, 6))
	plt.plot(np.linalg.norm(values, axis=1), color="tab:blue", linewidth=1.5)
	plt.title(f"{title} do {segment_name} ao longo do tempo")
	plt.xlabel("Frames")
	plt.ylabel(ylabel)
	plt.grid()
	plt.show()


def _plot_components(data, segment_name, getter, title, ylabel):
	values = np.asarray(getter(segment_name), dtype=float)
	if values.ndim != 2 or values.shape[1] != 3:
		raise ValueError("Os dados do segmento devem ter o formato (frames, 3).")
	if not np.isfinite(values).all():
		raise ValueError("Os dados do segmento contêm valores não finitos.")
	plt.figure(figsize=(10, 6))
	for index, color, label in ((0, "tab:red", "Componente X"), (1, "tab:green", "Componente Y"), (2, "tab:blue", "Componente Z")):
		plt.plot(values[:, index], color=color, linewidth=1.5, label=label)
	plt.title(f"Componentes {title} do {segment_name} ao longo do tempo")
	plt.xlabel("Frames")
	plt.ylabel(ylabel)
	plt.legend()
	plt.grid()
	plt.show()


def plot_segment_scalar_velocity(data, segment_name):
	_plot_scalar(data, segment_name, data.get_segment_velocity, "Velocidade escalar", "Velocidade (m/s)")


def plot_segment_scalar_acceleration(data, segment_name):
	_plot_scalar(data, segment_name, data.get_segment_acceleration, "Aceleração escalar", "Aceleração (m/s²)")


def plot_segment_scalar_angular_velocity(data, segment_name):
	_plot_scalar(data, segment_name, data.get_segment_angular_velocity, "Velocidade angular escalar", "Velocidade angular (rad/s)")


def plot_segment_scalar_angular_acceleration(data, segment_name):
	_plot_scalar(data, segment_name, data.get_segment_angular_acceleration, "Aceleração angular escalar", "Aceleração angular (rad/s²)")


def plot_segment_velocity_components(data, segment_name):
	_plot_components(data, segment_name, data.get_segment_velocity, "da velocidade", "Velocidade (m/s)")


def plot_segment_acceleration_components(data, segment_name):
	_plot_components(data, segment_name, data.get_segment_acceleration, "da aceleração", "Aceleração (m/s²)")


__all__ = [name for name in globals() if name.startswith("plot_")]
