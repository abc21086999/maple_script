import pytest

RUNE_BGR = (255, 102, 221)   # 與 MapleVision.rune_color 相同


def paint(img, y, x, size, color=RUNE_BGR):
    out = img.copy()
    out[y:y + size, x:x + size] = color
    return out


class TestHasRune:

    def test_blank_map_has_no_rune(self, vision, blank_minimap):
        assert vision.has_rune(img_np=blank_minimap) is False

    def test_rune_block_is_detected(self, vision, blank_minimap):
        img = paint(blank_minimap, y=40, x=100, size=4)
        assert vision.has_rune(img_np=img) is True

    def test_single_pixel_noise_is_ignored(self, vision, blank_minimap):
        img = paint(blank_minimap, y=40, x=100, size=1)
        assert vision.has_rune(img_np=img) is False

    @pytest.mark.parametrize("size, expected", [(2, False), (3, True)])
    def test_erosion_size_boundary(self, vision, blank_minimap, size, expected):
        """3x3 腐蝕：2x2 的色塊會被濾掉，3x3 剛好留下"""
        img = paint(blank_minimap, y=40, x=100, size=size)
        assert vision.has_rune(img_np=img) is expected

    def test_other_colors_are_not_rune(self, vision, blank_minimap):
        img = paint(blank_minimap, y=40, x=100, size=6, color=(118, 45, 253))  # 其他玩家的紅點
        assert vision.has_rune(img_np=img) is False

    @pytest.mark.parametrize("offset, expected", [
        (5, True),    # 每個通道差 5，總差 15 < 30
        (10, False),  # 每個通道差 10，總差 30，不小於 30
    ])
    def test_color_tolerance_boundary(self, vision, blank_minimap, offset, expected):
        near = tuple(c - offset for c in RUNE_BGR)
        img = paint(blank_minimap, y=40, x=100, size=4, color=near)
        assert vision.has_rune(color_tolerance=10, img_np=img) is expected

    def test_larger_tolerance_accepts_more_variation(self, vision, blank_minimap):
        near = tuple(c - 10 for c in RUNE_BGR)
        img = paint(blank_minimap, y=40, x=100, size=4, color=near)
        assert vision.has_rune(color_tolerance=11, img_np=img) is True

    def test_returns_none_when_minimap_not_available(self, vision, mocker):
        """沒有傳圖時會自己截圖；截圖失敗（小地圖沒開）要回傳 None"""
        mocker.patch.object(vision, "get_mini_map_area_screenshot", return_value=None)
        assert vision.has_rune() is None

    def test_captures_by_itself_when_no_image_given(self, vision, blank_minimap, mocker):
        grab = mocker.patch.object(vision, "get_mini_map_area_screenshot",
                                   return_value=paint(blank_minimap, 40, 100, 4))
        assert vision.has_rune() is True
        grab.assert_called_once()