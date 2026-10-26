import pytest

CHARACTER_BGR = (12, 240, 239)   # 與 MapleVision.my_character_color 相同


def paint(img, y, x, size, color=CHARACTER_BGR):
    out = img.copy()
    out[y:y + size, x:x + size] = color
    return out


class TestGetCharacterPosition:

    def test_no_character_returns_not_found(self, vision, blank_minimap):
        assert vision.get_character_position(img_np=blank_minimap) == "not_found"

    @pytest.mark.parametrize("x, expected", [
        (10, "left"),
        (99, "left"),     # 圖寬 200，中線是 100，小於中線算左邊
        (100, "right"),   # 剛好在中線算右邊
        (190, "right"),
    ])
    def test_position_relative_to_center_line(self, vision, blank_minimap, x, expected):
        img = paint(blank_minimap, y=50, x=x, size=1)
        assert vision.get_character_position(img_np=img) == expected

    def test_uses_average_position_not_majority(self, vision, blank_minimap):
        """兩個點在左邊、一個點在最右邊：平均 x 約 73，仍然是左邊"""
        img = paint(blank_minimap, y=50, x=10, size=1)
        img = paint(img, y=50, x=20, size=1)
        img = paint(img, y=50, x=190, size=1)
        assert vision.get_character_position(img_np=img) == "left"

    def test_character_body_larger_than_one_pixel(self, vision, blank_minimap):
        img = paint(blank_minimap, y=40, x=140, size=6)
        assert vision.get_character_position(img_np=img) == "right"

    def test_other_colors_are_not_character(self, vision, blank_minimap):
        img = paint(blank_minimap, y=20, x=50, size=6, color=(118, 45, 253))    # 其他玩家（紅）
        img = paint(img, y=60, x=150, size=6, color=(255, 102, 221))           # 輪（紫）
        assert vision.get_character_position(img_np=img) == "not_found"

    @pytest.mark.parametrize("offset, expected", [
        (5, "left"),        # 每個通道差 5，總差 15 < 90
        (30, "not_found"),  # 每個通道差 30，總差 90，不小於 90
    ])
    def test_color_tolerance_boundary(self, vision, blank_minimap, offset, expected):
        near = (CHARACTER_BGR[0] + offset, CHARACTER_BGR[1] - offset, CHARACTER_BGR[2] - offset)
        img = paint(blank_minimap, y=50, x=20, size=1, color=near)
        assert vision.get_character_position(color_tolerance=30, img_np=img) == expected

    def test_returns_not_found_when_minimap_not_available(self, vision, mocker):
        """小地圖沒開、截圖失敗時，應該回傳 not_found，而不是丟例外"""
        mocker.patch.object(vision, "get_mini_map_area_screenshot", return_value=None)
        assert vision.get_character_position() is None

    def test_captures_by_itself_when_no_image_given(self, vision, blank_minimap, mocker):
        grab = mocker.patch.object(vision, "get_mini_map_area_screenshot",
                                   return_value=paint(blank_minimap, y=50, x=150, size=3))
        assert vision.get_character_position() == "right"
        grab.assert_called_once()