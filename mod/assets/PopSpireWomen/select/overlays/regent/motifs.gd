extends RefCounted
## Authored star diagrams, informed by the seven local v0.107.1 atlas outlines.
## Names/order are NRegentCharacterSelectBg._Ready callback order, not lore.
## Source mapping and deliberate visual changes: docs/development/regent-overlay.md.

const SKINS = [
	"spheric guardian constellation", "deca outline", "sentry constellation",
	"snecko constellation", "cultist constellation", "shapes constellation",
	"amogus constellation",
]
const POSITIONS = [
	Vector2(1255, 265), Vector2(900, 310), Vector2(575, 610),
	Vector2(960, 945), Vector2(2070, 485), Vector2(2070, 805), Vector2(620, 270),
]
const RADII = [
	Vector2(92, 92), Vector2(112, 88), Vector2(62, 124),
	Vector2(115, 93), Vector2(98, 83), Vector2(75, 85), Vector2(47, 55),
]
# A small fixed sky; no random calls or global/game RNG state.
const SKY = [
	Vector2(535, 360), Vector2(721, 220), Vector2(789, 382), Vector2(1028, 207),
	Vector2(1112, 365), Vector2(1350, 166), Vector2(1490, 232), Vector2(1386, 369),
	Vector2(590, 445), Vector2(503, 763), Vector2(638, 855), Vector2(790, 917),
	Vector2(682, 1022), Vector2(829, 1070), Vector2(1102, 877), Vector2(1992, 298),
	Vector2(2178, 246), Vector2(2044, 374), Vector2(2156, 645), Vector2(2005, 716),
	Vector2(2156, 918), Vector2(1984, 1015), Vector2(2028, 570), Vector2(721, 330),
]

static func _line(coords: Array) -> PackedVector2Array:
	var points := PackedVector2Array()
	for i in range(0, coords.size(), 2): points.append(Vector2(coords[i], coords[i + 1]))
	return points

static func _circle(center: Vector2, radius: float) -> PackedVector2Array:
	var points := PackedVector2Array()
	for i in 17: points.append(center + Vector2.from_angle(TAU * i / 16.0) * radius)
	return points

static func paths(index: int) -> Array[PackedVector2Array]:
	match index:
		0: # Spheric Guardian: three curled sectors and three satellites.
			var result: Array[PackedVector2Array] = []
			var curl := _line([-.60,-.24, -.57,-.52, -.29,-.72, .08,-.76, .42,-.61,
				.67,-.34, .39,-.42, .15,-.32, .07,-.10, .18,.04, .28,-.03])
			for i in 3:
				var rotated := PackedVector2Array()
				for point in curl: rotated.append(point.rotated(TAU * i / 3.0))
				result.append(rotated)
				result.append(_circle(Vector2.from_angle(-2.25 + TAU * i / 3.0), .115))
			return result
		1: # Deca: angular body and extended limbs, not a generic diamond.
			return [_line([-.29,-.62, .35,-.68, .49,.06, -.10,.39, .02,.70,
				-.29,.98, -.18,.59, -.34,.39, -.55,.35, -.76,.68, -.78,.20,
				-.31,.08, -.29,-.62]),
				_line([-.30,-.25, -.88,-.39, -.87,-.76, -.43,-1.02, -.66,-.62, -.30,-.36]),
				_line([.31,.18, .49,.52, 1.04,.61, .44,.82, .21,.26])]
		2: # Sentry: two opposed pointed bodies, joined by a central eye.
			return [_line([.73,-1, -.66,-.28, .40,-.06, .73,-1, .04,-.33, -.66,-.28]),
				_line([.04,-.33, .40,-.06]), _circle(Vector2(-.11, -.05), .16),
				_line([-.20,.03, -.88,.03, -.99,.96, .46,.35, -.20,.03, -.99,.96])]
		3: # Snecko: long bent neck, curled tail, eye and two feet.
			return [_line([-.65,-.36, -.68,-.66, -.52,-.82, -.32,-.79, -.10,-1.02,
				.18,-1.10, .38,-.96, .44,-.70, .38,-.17, .52,.13, .83,.08,
				1.0,.20, 1.04,.45, .80,.73, .36,.81, -.01,.72, -.13,.43,
				-.17,.03, .00,-.46, .00,-.63, -.24,-.45, -.43,-.22, -.65,-.18, -.65,-.36]),
				_line([-.14,.33, -.44,.45, -.63,.36, -.83,.40, -.98,.63, -.77,.58,
				-.57,.72, -.32,.64, -.14,.52]),
				_line([-.57,-.47, -.50,-.63, -.43,-.66, -.45,-.52, -.57,-.47]),
				_line([-.13,.55, -.28,.69, -.29,.93, -.47,1.01]),
				_line([-.42,.89, -.29,.93, -.20,1.06]),
				_line([.51,.51, .65,.59, .69,.96, .55,1.06]),
				_line([.87,1.04, .69,.96, .77,1.12])]
		4: # Cultist: broad bird head, long open beak and eye.
			return [_line([-1.02,-.77, -.73,-.87, -.36,-.72, -.05,-.47,
				.31,-.40, .64,-.49, .86,-.27, 1.0,.12, .91,.47, .64,.61,
				.47,.81, .27,.78, .16,.65, -.01,.76, -.19,.61, -.33,.63,
				-.43,.33, -.70,.04, -.97,-.48, -.62,-.16, -.19,.02, -.09,-.01,
				-.28,-.15, -.64,-.37, -1.02,-.77]), _circle(Vector2(.16, -.16), .09)]
		5: # Shapes: a faceted fan around a round centre; no invented zodiac.
			return [_line([-.22,-.89, .15,-.82, .65,-.64, 1.0,.05, .72,.80,
				-.05,1.03, -.64,.73, -.85,.10, -.71,-.45, -.22,-.89]),
				_circle(Vector2(-.04, .02), .18),
				_line([-.22,-.89, -.12,-.14]), _line([.65,-.64, .09,-.10]),
				_line([1.0,.05, .14,.04]), _line([.72,.80, .08,.15]),
				_line([-.05,1.03, -.04,.20]), _line([-.64,.73, -.17,.14])]
		6: # Amogus: compact figure, backpack, visor, separated legs.
			return [_line([-.52,-.59, -.32,-.91, .08,-1.0, .43,-.86, .56,-.56,
				.44,-.27, .61,-.12, .45,.96, .10,.98, .07,.56, -.15,.53,
				-.23,.86, -.66,.76, -.68,.43, -.52,-.59]),
				_line([-.55,-.57, -.89,-.49, -1.02,.27, -.70,.44]),
				_line([.12,-.53, .47,-.53, .77,-.36, .75,-.16, .47,-.06,
				.08,-.19, -.05,-.37, .12,-.53])]
	return []
