"""SVG path data flattened into rings, and a drawn charge tested by point."""

from __future__ import annotations

import pytest

from ars_magica_manager import arms, artwork, svg_paths


def test_lines_and_relative_moves_make_rings():
    found = svg_paths.rings("M0 0 L10 0 L10 10 Z m2 2 h4 v4 h-4 z")
    assert found == [
        ((0.0, 0.0), (10.0, 0.0), (10.0, 10.0)),
        ((2.0, 2.0), (6.0, 2.0), (6.0, 6.0), (2.0, 6.0)),
    ]
    # Pairs after a move are lines.
    assert svg_paths.rings("M0 0 5 0 5 5z") == [((0.0, 0.0), (5.0, 0.0), (5.0, 5.0))]


def test_curves_and_arcs_are_cut_into_steps():
    (curve,) = svg_paths.rings("M0 0 C0 10 10 10 10 0 Z")
    assert len(curve) == svg_paths.STEPS + 1 and curve[-1] == pytest.approx((10, 0))
    assert max(y for _x, y in curve) == pytest.approx(7.5)
    # A smooth curve mirrors the last control point.
    (smooth,) = svg_paths.rings("M0 0 C0 10 10 10 10 0 S20 -10 20 0 Z")
    assert min(y for _x, y in smooth) == pytest.approx(-7.5)
    (circle,) = svg_paths.rings("M10 0 A10 10 0 1 1 -10 0 A10 10 0 1 1 10 0 Z")
    ys = [y for _x, y in circle]
    assert min(ys) == pytest.approx(-10, abs=0.1) and max(ys) == pytest.approx(
        10, abs=0.1
    )


def test_bad_path_data_is_refused():
    with pytest.raises(ValueError, match="starts with a number"):
        svg_paths.rings("10 10 L 0 0")


def test_a_drawn_charge_fills_even_odd():
    # A square with a square hole, fitted from a 0..20 box.
    ring = arms.drawing("M0 0 H20 V20 H0 Z M5 5 H15 V15 H5 Z", (0, 0, 20, 20))
    assert ring.contains(0.1, 0.1)
    assert not ring.contains(0.5, 0.5)
    assert not ring.contains(1.1, 0.5)
    # A wide box is centred in the unit square.
    (wide,) = svg_paths.fitted("M0 0 H20 V10 H0 Z", (0, 0, 20, 10))
    assert wide[0] == (0.0, 0.25) and wide[2] == (1.0, 0.75)


def test_open_subpaths_are_kept_when_asked():
    # A stroke's single line has only two points.
    assert svg_paths.rings("M0 0 L5 5") == []
    assert svg_paths.rings("M0 0 L5 5", shortest=2) == [((0.0, 0.0), (5.0, 5.0))]


def test_the_lion_is_drawn_in_three_layers(tmp_path):
    lion = arms.layers(artwork.CHARGE_DRAWINGS["Lion"])
    assert set(lion) == {"body", "lines", "armed"}
    assert arms.CHARGE_SHAPES["Lion"] == (lion["body"],)
    # Its chest is in the silhouette, the corner of its square is not.
    assert lion["body"].contains(0.5, 0.5)
    assert not lion["body"].contains(0.02, 0.98)
    # A file with no viewBox is refused.
    bad = tmp_path / "bad.svg"
    bad.write_text(
        '<svg><path id="body" d="M0 0 L1 0 L1 1 Z"/></svg>', encoding="utf-8"
    )
    with pytest.raises(ValueError, match="viewBox"):
        arms.layers(bad)


def test_line_work_and_claws_take_a_contrasting_tincture():
    gold = arms.Arms("Azure", charge="Lion", charge_tincture="Or")
    assert arms.line_tincture(gold) == "Sable" and arms.armed_tincture(gold) == "Gules"
    black = arms.Arms("Or", charge="Lion", charge_tincture="Sable")
    assert arms.line_tincture(black) == "Argent"
    assert (
        arms.armed_tincture(arms.Arms("Or", charge="Lion", charge_tincture="Gules"))
        == "Azure"
    )
    assert (
        arms.armed_tincture(arms.Arms("Gules", charge="Lion", charge_tincture="Or"))
        == "Azure"
    )
