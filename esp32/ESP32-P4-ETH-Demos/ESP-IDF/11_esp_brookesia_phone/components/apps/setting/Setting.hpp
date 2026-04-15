/*
 * SPDX-FileCopyrightText: 2023 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */
#pragma once

#include <array>
#include <map>
#include <string>
#include "esp_event.h"
#include "lvgl.h"
#include "esp_brookesia.hpp"

class AppSettings: public ESP_Brookesia_PhoneApp {
public:
    AppSettings();
    ~AppSettings();

    bool run(void);
    bool back(void);
    bool close(void);

    bool init(void) override;
    bool pause(void) override;
    bool resume(void) override;

private:
    typedef enum {
        UI_MAIN_SETTING_INDEX = 0,
        UI_BLUETOOTH_SETTING_INDEX,
        UI_VOLUME_SETTING_INDEX,
        UI_BRIGHTNESS_SETTING_INDEX,
        UI_ABOUT_SETTING_INDEX,
        UI_MAX_INDEX,
    } SettingScreenIndex_t;

    /* Operations */
    // UI
    void extraUiInit(void);
    // NVS Parameters
    bool loadNvsParam(void);
    bool setNvsParam(std::string key, int value);
    void updateUiByNvsParam(void);
    // Smart Gadget
    // void updateGadgetTime(struct tm timeinfo);

    /* Task */
    static void euiRefresTask(void *arg);

    /* Event Handler */
    /* UI Event Callback */
    // Main
    static void onScreenLoadEventCallback( lv_event_t * e);
    // Bluetooth
    static void onSwitchPanelScreenSettingBLESwitchValueChangeEventCallback( lv_event_t * e);
    // Audio
    static void onSliderPanelVolumeSwitchValueChangeEventCallback( lv_event_t * e);
    // Brightness
    static void onSliderPanelLightSwitchValueChangeEventCallback( lv_event_t * e);

    bool _is_ui_resumed;
    bool _is_ui_del;
    SettingScreenIndex_t _screen_index;
    std::array<lv_obj_t *, UI_MAX_INDEX> _screen_list;
    std::map<std::string, int32_t> _nvs_param_map;
    const ESP_Brookesia_StatusBar *status_bar; 
    const ESP_Brookesia_RecentsScreen *backstage;
};
