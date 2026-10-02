"""Classificação ergonômica em semáforo segundo a DGUV Information 208-033, Anexo 3
(IFA, set/2015; antiga BGI/GUV-I 7011).


* Cada regra lista apenas as faixas aceitáveis (verde), condicionais (amarelo) e,
  nas tabelas de momentos, elevadas (laranja). Tudo fora dessas faixas é VERMELHO,
  o que reproduz os "< x" e "> y" vermelhos.
* se um valor cai exatamente na fronteira entre duas faixas (ex.: 25° na inclinação da cabeça),
  vale a menos severa (verde < amarelo < laranja). Vermelho só começa estritamente além do limite.
* A norma não considera duração, frequência, dinâmica nem apoio do corpo/braço.
"""

import math
from collections import Counter
from dataclasses import dataclass, replace
from typing import Iterable, Sequence


GREEN, YELLOW, ORANGE, RED = "green", "yellow", "orange", "red"
ZONE_ORDER = (GREEN, YELLOW, ORANGE, RED)
COLORS = {GREEN: "#7CFC00", YELLOW: "#FFD700", ORANGE: "#FFA500", RED: "#FF4444"}
ZONE_LABELS = {
	GREEN: "Verde: neutro/aceitável",
	YELLOW: "Amarelo: condicionalmente aceitável",
	ORANGE: "Laranja: elevado",
	RED: "Vermelho: inaceitável",
}
INF = float("inf")


@dataclass(frozen=True)
class Band:
	"""Intervalo fechado [low, high] associado a uma zona de cor."""

	low: float
	high: float
	zone: str

	def __post_init__(self):
		if self.zone not in COLORS:
			raise ValueError(f"Zona desconhecida: {self.zone}")
		if self.low > self.high:
			raise ValueError(f"Faixa inválida: {self.low} > {self.high}")


@dataclass(frozen=True)
class JointRule:
	name: str
	positive: str
	negative: str
	reference: str
	bands: tuple[Band, ...]
	unit: str = "°"

	def classify(self, value: float) -> str:
		if math.isnan(value):
			raise ValueError("Não é possível classificar NaN.")
		matches = [band.zone for band in self.bands if band.low <= value <= band.high]
		if not matches:
			return RED
		return min(matches, key=ZONE_ORDER.index)

	@property
	def zones(self) -> tuple[str, ...]:
		"""Zonas presentes nesta regra (sempre inclui vermelho), da menos à mais severa."""
		present = {band.zone for band in self.bands} | {RED}
		return tuple(zone for zone in ZONE_ORDER if zone in present)

	@property
	def breakpoints(self) -> tuple[float, ...]:
		"""Todos os limites finitos da regra, em ordem crescente."""
		points = {p for band in self.bands for p in (band.low, band.high) if math.isfinite(p)}
		return tuple(sorted(points))

	def spans(self) -> tuple[Band, ...]:
		"""Faixas contíguas cobrindo (-inf, +inf), com os trechos vermelhos explícitos.
		Útil para sombrear o fundo do gráfico com axvspan."""
		result: list[Band] = []
		cursor = -INF
		for band in sorted(self.bands, key=lambda b: b.low):
			if band.low > cursor:
				result.append(Band(cursor, band.low, RED))
			result.append(band)
			cursor = max(cursor, band.high)
		if cursor < INF:
			result.append(Band(cursor, INF, RED))
		return tuple(result)

	def mirrored(self) -> "JointRule":
		"""Regra com o sinal invertido, para dados cuja convenção é oposta à do PDF."""
		flipped = tuple(Band(-b.high, -b.low, b.zone) for b in self.bands)
		return replace(self, bands=flipped, positive=self.negative, negative=self.positive)


def _angle(name, positive, negative, reference, *bands):
	return JointRule(name, positive, negative, reference, tuple(bands))


G, Y, O = GREEN, YELLOW, ORANGE

RULES: dict[str, JointRule] = {
	# ---- 1a) Cabeça e pescoço -------------------------------------------------
	"head_inclination": _angle(
		"Inclinação da cabeça", "flexão", "extensão", "ISO 11226",
		Band(0, 25, G), Band(25, 85, Y),
	),
	"head_lateral_inclination": _angle(
		"Inclinação lateral da cabeça", "direita", "esquerda", "EN 1005-4",
		Band(-10, 10, G),
	),
	"neck_torsion": _angle(
		"Torção do pescoço", "direita", "esquerda", "EN 1005-4",
		Band(-45, 45, G),
	),
	"neck_bending": _angle(
		"Flexão do pescoço", "flexão", "extensão", "ISO 11226",
		Band(0, 25, G),
	),
	# ---- 1b) Tronco -----------------------------------------------------------
	"trunk_inclination": _angle(
		"Inclinação do tronco", "flexão", "extensão", "ISO 11226 / EN 1005-4",
		Band(0, 20, G), Band(20, 60, Y),
	),
	"trunk_lateral_inclination": _angle(
		"Inclinação lateral do tronco", "direita", "esquerda", "ISO 11226 / Drury 1987",
		Band(-10, 10, G), Band(-20, -10, Y), Band(10, 20, Y),
	),
	"back_bending": _angle(
		"Flexão das costas", "flexão", "extensão", "avaliação própria / EN 1005-4",
		Band(0, 20, G), Band(20, 40, Y),
	),
	"back_torsion": _angle(
		"Torção das costas", "direita", "esquerda", "avaliação própria / EN 1005-4",
		Band(-10, 10, G), Band(-20, -10, Y), Band(10, 20, Y),
	),
	# ---- 1c) Ombro / braço ----------------------------------------------------
	"shoulder_abduction": _angle(
		"Abdução/adução do ombro", "adução", "abdução", "ISO 11226 / EN 1005-4",
		Band(-20, 0, G), Band(-60, -20, Y),
	),
	"shoulder_flexion": _angle(
		"Flexão/extensão do ombro", "flexão", "extensão", "EN 1005-4",
		Band(0, 20, G), Band(20, 60, Y),
	),
	"shoulder_rotation": _angle(
		"Rotação do ombro", "rotação interna", "rotação externa", "avaliação própria / Drury 1987",
		Band(-15, 30, G), Band(-30, -15, Y), Band(30, 60, Y),
	),
	# ---- 1d) Cotovelo, antebraço e mão ---------------------------------------
	"elbow_flexion": _angle(
		"Flexão/extensão do cotovelo", "flexão", "extensão", "McAtamney e Corlett 1993",
		Band(60, 100, G),
	),
	"forearm_rotation": _angle(
		"Pronação/supinação do antebraço", "pronação", "supinação", "Drury 1987",
		Band(-30, 20, G), Band(-55, -30, Y), Band(20, 40, Y),
	),
	"wrist_flexion": _angle(
		"Flexão/extensão do punho", "flexão", "extensão", "Drury 1987",
		Band(-25, 20, G), Band(-50, -25, Y), Band(20, 45, Y),
	),
	"wrist_deviation": _angle(
		"Desvio radial/ulnar do punho", "desvio radial", "desvio ulnar", "Drury 1987",
		Band(-10, 10, G), Band(-25, -10, Y), Band(10, 15, Y),
	),
	# ---- 1e) Joelho -----------------------------------------------------------
	"knee_seated": _angle(
		"Ângulo do joelho (sentado)", "flexão", "extensão", "ISO 11226",
		Band(45, 90, G), Band(0, 45, Y),
	),
	"knee_standing": _angle(
		"Ângulo do joelho (em pé)", "flexão", "extensão", "ISO 11226",
		Band(0, 5, G), Band(5, 10, Y),
	),
	"l5s1_moment": JointRule(
		"Momento em L5/S1", "", "", "Tichauer 1978",
		(Band(0, 40, G), Band(40, 80, Y), Band(80, 135, O)), unit="Nm",
	),
	# carga menor que a mínima da tabela, tratamos como verde.
	"l5s1_compression_male": JointRule(
		"Força compressiva em L5/S1 (homens)", "", "", "Dortmunder Richtwerte (Jäger et al. 2001)",
		(Band(0, 2.3, G), Band(2.3, 3.2, Y)), unit="kN",
	),
	"l5s1_compression_female": JointRule(
		"Força compressiva em L5/S1 (mulheres)", "", "", "Dortmunder Richtwerte (Jäger et al. 2001)",
		(Band(0, 1.8, G), Band(1.8, 2.5, Y)), unit="kN",
	),
	"shoulder_moment_sum": JointRule(
		"Soma dos momentos nos ombros", "", "", "Tichauer 1978",
		(Band(0, 40, G), Band(40, 80, Y), Band(80, 120, O)), unit="Nm",
	),
}


def get_rule(rule: "str | JointRule | None") -> "JointRule | None":
	if rule is None or isinstance(rule, JointRule):
		return rule
	try:
		return RULES[rule]
	except KeyError as error:
		valid = ", ".join(sorted(RULES))
		raise ValueError(f"Regra DGUV desconhecida: {rule!r}. Válidas: {valid}") from error


def make_bins(rule: JointRule, low: float, high: float, width: float = 5.0) -> list[float]:
	"""Limites de bins de largura `width` cobrindo [low, high], acrescidos dos limites da
	regra. Assim nenhuma barra do histograma atravessa uma fronteira de cor."""
	if width <= 0:
		raise ValueError("A largura do bin deve ser maior que zero.")
	if high < low:
		raise ValueError("high deve ser maior ou igual a low.")
	start = math.floor(low / width) * width
	stop = math.ceil(high / width) * width
	if stop == start:
		stop = start + width
	steps = int(round((stop - start) / width))
	edges = {round(start + i * width, 9) for i in range(steps + 1)}
	edges |= {round(p, 9) for p in rule.breakpoints if start < p < stop}
	return sorted(edges)


def color_histogram_patches(
	patches: Sequence[object], bin_edges: Sequence[float], rule: JointRule
) -> None:
	"""Pinta cada barra pela zona do centro do bin (use `make_bins` para que isso seja exato)."""
	for patch, left, right in zip(patches, bin_edges[:-1], bin_edges[1:]):
		patch.set_facecolor(COLORS[rule.classify((left + right) / 2)])


def time_in_zones(values: Iterable[float], rule: JointRule) -> dict[str, float]:
	"""Percentual das amostras em cada zona da regra."""
	values = tuple(values)
	if not values:
		return {zone: 0.0 for zone in rule.zones}
	counts = Counter(rule.classify(float(value)) for value in values)
	return {zone: counts.get(zone, 0) / len(values) * 100 for zone in rule.zones}


def legend_handles(rule: JointRule) -> list:
	"""Patches para `plt.legend(handles=...)`, só com as zonas que a regra usa."""
	from matplotlib.patches import Patch

	return [
		Patch(facecolor=COLORS[zone], edgecolor="black", label=ZONE_LABELS[zone])
		for zone in rule.zones
	]


__all__ = [
	"Band", "JointRule", "GREEN", "YELLOW", "ORANGE", "RED", "COLORS", "ZONE_LABELS",
	"INF", "RULES", "get_rule", "make_bins", "color_histogram_patches", "time_in_zones",
	"legend_handles",
]