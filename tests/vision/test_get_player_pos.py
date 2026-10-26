import pytest

CHARACTER_BGR = (12, 240, 239)   # 與 MapleVision.my_character_color 相同


def paint(img_np, y, x, size, color=CHARACTER_BGR):
    out = img_np.copy()
    out[y:y + size, x:x + size] = color
    return out


class TestGetPlayerPos:

    def test_blank_map_returns_none(self, vision, blank_minimap):
        assert vision.get_player_pos(img_np=blank_minimap) is None

    def test_returns_center_of_character_block(self, vision, blank_minimap):
        img_np = paint(blank_minimap, y=40, x=100, size=5)   # 涵蓋 x=100~104, y=40~44
        assert vision.get_player_pos(img_np=img_np) == (102, 42)

    def test_coordinates_are_x_then_y(self, vision, blank_minimap):
        img_np = paint(blank_minimap, y=30, x=150, size=5)
        assert vision.get_player_pos(img_np=img_np) == (152, 32)

    @pytest.mark.parametrize("size, expected", [
        (1, None),          # 單一像素的輪廓面積為 0，算不出重心
        (2, (100, 40)),     # 2x2 起算得出來，座標被 int() 無條件捨去
    ])
    def test_minimum_detectable_size(self, vision, blank_minimap, size, expected):
        img_np = paint(blank_minimap, y=40, x=100, size=size)
        assert vision.get_player_pos(img_np=img_np) == expected

    def test_picks_the_largest_blob(self, vision, blank_minimap):
        img_np = paint(blank_minimap, y=20, x=20, size=3)    # 小的
        img_np = paint(img_np, y=60, x=150, size=7)          # 大的
        assert vision.get_player_pos(img_np=img_np) == (153, 63)

    def test_other_colors_are_not_character(self, vision, blank_minimap):
        img_np = paint(blank_minimap, y=20, x=50, size=6, color=(118, 45, 253))    # 其他玩家（紅）
        img_np = paint(img_np, y=60, x=150, size=6, color=(255, 102, 221))        # 輪（紫）
        assert vision.get_player_pos(img_np=img_np) is None

    @pytest.mark.parametrize("offset, expected", [
        (9, (102, 42)),   # 每個通道差 9，總差 27 < 30
        (10, None),       # 每個通道差 10，總差 30，不小於 30
    ])
    def test_color_tolerance_boundary(self, vision, blank_minimap, offset, expected):
        """這個函式的容忍度是寫死的 30，沒有參數可調"""
        near = (CHARACTER_BGR[0] + offset, CHARACTER_BGR[1] - offset, CHARACTER_BGR[2] - offset)
        img_np = paint(blank_minimap, y=40, x=100, size=5, color=near)
        assert vision.get_player_pos(img_np=img_np) == expected

    def test_returns_none_when_minimap_not_available(self, vision, mocker):
        """沒有傳圖時會自己截圖；截圖失敗（小地圖沒開）要回傳 None"""
        mocker.patch.object(vision, "get_mini_map_area_screenshot", return_value=None)
        assert vision.get_player_pos() is None

    def test_captures_by_itself_when_no_image_given(self, vision, blank_minimap, mocker):
        grab = mocker.patch.object(vision, "get_mini_map_area_screenshot",
                                   return_value=paint(blank_minimap, y=40, x=100, size=5))
        assert vision.get_player_pos() == (102, 42)
        grab.assert_called_once()