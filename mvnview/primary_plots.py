import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from .dguv import (
	COLORS,
	color_histogram_patches,
	get_rule,
	legend_handles,
	make_bins,
	time_in_zones,
)

_BIN_WIDTHS = (10, 5, 2.5, 2, 1, 0.5)
_ZONE_SHORT_NAMES = {"green": "Verde", "yellow": "Amarelo", "orange": "Laranja", "red": "Vermelho"}


def _time_axis(frame_count, fps):
	if fps <= 0:
		raise ValueError("O valor de fps deve ser maior que zero.")
	return np.arange(frame_count) / fps


def _histogram_bins(values, attr_bins, rule):
	# Bins do histograma. Sem regra, devolve attr_bins como veio. Com regra, garante que
	# nenhuma barra atravesse uma fronteira de cor da norma.
	if rule is None:
		return attr_bins
	if np.ndim(attr_bins) == 0:
		low, high = float(values.min()), float(values.max())
		count = len(np.histogram_bin_edges(values, bins=attr_bins)) - 1
		raw_width = (high - low) / count or 1.0
		fitting = [
			width for width in _BIN_WIDTHS
			if all(abs(point / width - round(point / width)) < 1e-9 for point in rule.breakpoints)
		]
		width = min(fitting or (raw_width,), key=lambda candidate: abs(candidate - raw_width))
		return make_bins(rule, low, high, width)
	edges = np.asarray(attr_bins, dtype=float)
	inside = [point for point in rule.breakpoints if edges[0] < point < edges[-1]]
	return np.unique(np.concatenate([edges, inside]))


def _plot_joint_angle_histogram(data, segment_name, component, angle_name, attr_bins, title, rule=None):
	values = np.asarray(data.get_joint_angle_xzy(segment_name)[:, component], dtype=float)
	if values.ndim != 1:
		raise ValueError(f"O ângulo de {angle_name} deve ter o formato (frames,).")
	if not np.isfinite(values).all():
		raise ValueError(f"O ângulo de {angle_name} contém valores não finitos.")
	if values.size == 0:
		raise ValueError(f"O ângulo de {angle_name} não contém frames.")
	rule = get_rule(rule)
	fig, ax = plt.subplots(figsize=(10, 6))
	weights = np.full(values.size, 100 / values.size)
	percentages, edges, patches = ax.hist(
		values, bins=_histogram_bins(values, attr_bins, rule), weights=weights,
		color="skyblue", edgecolor="black",
	)
	if rule is not None:
		color_histogram_patches(patches, edges, rule)
		ax.legend(handles=legend_handles(rule))
	for percentage, patch in zip(percentages, patches):
		if percentage > 0:
			ax.text(
				patch.get_x() + patch.get_width() / 2,
				percentage / 2,
				f"{percentage:.1f}%",
				ha="center", va="center", fontsize=8,
			)
	ax.set_title(title)
	ax.set_xlabel("Ângulo (°)")
	ax.set_ylabel("Tempo (%)")
	ax.grid(axis="y")
	plt.show()


def plot_abduction_histogram(data, segment_name, attr_bins, title, rule=None):
	_plot_joint_angle_histogram(data, segment_name, 0, "abdução", attr_bins, title, rule)


def plot_rotation_histogram(data, segment_name, attr_bins, title, rule=None):
	_plot_joint_angle_histogram(data, segment_name, 1, "rotação", attr_bins, title, rule)


def plot_flexion_histogram(data, segment_name, attr_bins, title, rule=None):
	_plot_joint_angle_histogram(data, segment_name, 2, "flexão", attr_bins, title, rule)

def _plot_joint_angle_byframe(data, segment_name, component, angle_name, title, fps, rule):
	values = np.asarray(data.get_joint_angle_xzy(segment_name)[:, component], dtype=float)
	if values.ndim != 1:
		raise ValueError(f"O ângulo de {angle_name} deve ter o formato (frames,).")
	if not np.isfinite(values).all():
		raise ValueError(f"O ângulo de {angle_name} contém valores não finitos.")
	time = _time_axis(len(values), fps)
	rule = get_rule(rule)
	fig, ax = plt.subplots(figsize=(10, 6))
	if rule is not None:
		bounds = (*rule.breakpoints, float(values.min()), float(values.max()))
		span = max(bounds) - min(bounds)
		padding = max(span * 0.05, 1.0)
		y_min, y_max = min(bounds) - padding, max(bounds) + padding
		ax.set_ylim(y_min, y_max)
		for band in rule.spans():
			lower, upper = max(band.low, y_min), min(band.high, y_max)
			if lower < upper:
				ax.axhspan(lower, upper, facecolor=COLORS[band.zone], alpha=0.7, zorder=0)
	ax.plot(time, values, color="black", linewidth=1.5, zorder=2)
	ax.set_title(title)
	ax.set_xlabel("Tempo (s)")
	ax.set_ylabel("Ângulo (°)")
	ax.grid(axis="x")
	if rule is not None:
		percentages = time_in_zones(values, rule)
		fig.subplots_adjust(right=0.72)
		handles = [
			Patch(
				facecolor=COLORS[zone], edgecolor="#444444",
				label=f"{_ZONE_SHORT_NAMES[zone]}   {percentages[zone]:.1f}%",
			)
			for zone in percentages
		]
		legend = ax.legend(
			handles=handles,
			loc="center left",
			bbox_to_anchor=(1.02, 0.5),
			title="Tempo por zona",
			frameon=True,
			fancybox=True,
			framealpha=0.95,
			edgecolor="#777777",
		)
		legend.get_frame().set_linewidth(0.8)
	plt.show()


def plot_abduction_byframe(data, segment_name, title, fps=60, rule=None):
	_plot_joint_angle_byframe(data, segment_name, 0, "abdução", title, fps, rule)


def plot_rotation_byframe(data, segment_name, title, fps=60, rule=None):
	_plot_joint_angle_byframe(data, segment_name, 1, "rotação", title, fps, rule)


def plot_flexion_byframe(data, segment_name, title, fps=60, rule=None):
	_plot_joint_angle_byframe(data, segment_name, 2, "flexão", title, fps, rule)




def plot_segment_position(data, segment_name, title):
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
	ax.set_title(title)
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


def plot_flat_segment_position(data, segment_name, title):
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
	ax.set_title(title)
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


def _plot_scalar(data, segment_name, getter, title, ylabel, fps):
	values = np.asarray(getter(segment_name), dtype=float)
	if values.ndim != 2 or values.shape[1] != 3:
		raise ValueError("Os dados do segmento devem ter o formato (frames, 3).")
	if not np.isfinite(values).all():
		raise ValueError("Os dados do segmento contêm valores não finitos.")
	time = _time_axis(values.shape[0], fps)
	plt.figure(figsize=(10, 6))
	plt.plot(time, np.linalg.norm(values, axis=1), color="tab:blue", linewidth=1.5)
	plt.title(title)
	plt.xlabel("Tempo (s)")
	plt.ylabel(ylabel)
	plt.grid()
	plt.show()


def _plot_components(data, segment_name, getter, title, ylabel, fps):
	values = np.asarray(getter(segment_name), dtype=float)
	if values.ndim != 2 or values.shape[1] != 3:
		raise ValueError("Os dados do segmento devem ter o formato (frames, 3).")
	if not np.isfinite(values).all():
		raise ValueError("Os dados do segmento contêm valores não finitos.")
	time = _time_axis(values.shape[0], fps)
	plt.figure(figsize=(10, 6))
	for index, color, label in ((0, "tab:red", "Componente X"), (1, "tab:green", "Componente Y"), (2, "tab:blue", "Componente Z")):
		plt.plot(time, values[:, index], color=color, linewidth=1.5, label=label)
	plt.title(title)
	plt.xlabel("Tempo (s)")
	plt.ylabel(ylabel)
	plt.legend()
	plt.grid()
	plt.show()



def plot_segment_scalar_velocity(data, segment_name, title, fps=60):
	_plot_scalar(data, segment_name, data.get_segment_velocity, title, "Velocidade (m/s)", fps)


def plot_segment_scalar_acceleration(data, segment_name, title, fps=60):
	_plot_scalar(data, segment_name, data.get_segment_acceleration, title, "Aceleração (m/s²)", fps)


def plot_segment_scalar_angular_velocity(data, segment_name, title, fps=60):
	_plot_scalar(data, segment_name, data.get_segment_angular_velocity, title, "Velocidade angular (rad/s)", fps)


def plot_segment_scalar_angular_acceleration(data, segment_name, title, fps=60):
	_plot_scalar(data, segment_name, data.get_segment_angular_acceleration, title, "Aceleração angular (rad/s²)", fps)


def plot_segment_velocity_components(data, segment_name, title, fps=60):
	_plot_components(data, segment_name, data.get_segment_velocity, title, "Velocidade (m/s)", fps)


def plot_segment_acceleration_components(data, segment_name, title, fps=60):
	_plot_components(data, segment_name, data.get_segment_acceleration, title, "Aceleração (m/s²)", fps)


__all__ = [name for name in globals() if name.startswith("plot_")]