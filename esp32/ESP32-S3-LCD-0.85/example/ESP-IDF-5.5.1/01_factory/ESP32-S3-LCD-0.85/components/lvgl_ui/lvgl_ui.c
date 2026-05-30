#include "lvgl_ui.h"
#include "tileview/system_tile.h"
#include "tileview/rgb_tile.h"
#include "tileview/wifi_tile.h"
lv_obj_t *tileview;
void lvgl_ui_init(void)
{
    tileview = lv_tileview_create(lv_scr_act());
    lv_obj_set_style_bg_opa(tileview, LV_OPA_0, LV_PART_SCROLLBAR | LV_STATE_DEFAULT);
    lv_obj_set_style_bg_opa(tileview, LV_OPA_0, LV_PART_SCROLLBAR | LV_STATE_SCROLLED);


    /*Tile1: just a label*/
    lv_obj_t *rgb_tile = lv_tileview_add_tile(tileview, 0, 0, LV_DIR_RIGHT);
    rgb_tile_init(rgb_tile);

    lv_obj_t *system_tile = lv_tileview_add_tile(tileview, 1, 0, LV_DIR_LEFT | LV_DIR_RIGHT);
    system_tile_init(system_tile);
    
    lv_obj_t *wifi_tile = lv_tileview_add_tile(tileview, 2, 0, LV_DIR_LEFT | LV_DIR_RIGHT);
    wifi_tile_init(wifi_tile);


}