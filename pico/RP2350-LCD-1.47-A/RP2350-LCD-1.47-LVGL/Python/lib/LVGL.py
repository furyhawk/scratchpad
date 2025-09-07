import sys
sys.path.append('.')
import lvgl as lv
import lv_utils
import time
import uctypes
import machine
import rp2
import gc

lv.deinit()
lv_utils.event_loop().deinit()

class LVGL(object):
    def disp_drv_flush_cb(self,disp_drv,area,color_p):

        # pos and data
        w = area.x2 - area.x1 + 1
        h = area.y2 - area.y1 + 1
        size = w * h
        data_view = color_p.__dereference__(size * self.pixel_size)
        self.rgb565_swap_func(data_view, size)
        
        # Set windows
        self.LCD.setWindows(area.x1, area.y1, area.x2+1, area.y2+1)
        self.LCD.cs.value(0)
        self.LCD.dc.value(1)
        
        # send data
        SPI0_BASE = 0x40080000 # FIXME: will be different for another SPI bus?
        SSPDR     = 0x008
        self.dma.config(
            read   = uctypes.addressof(data_view),
            write  = SPI0_BASE+SSPDR,
            count  = len(data_view),
            ctrl   = self.dma.pack_ctrl(size=0, treq_sel=24, inc_read=True, inc_write=False),
            trigger=  True
        )

        while self.dma.active():
            pass
        
#         self.LCD.spi.write(data_view)
        
        self.LCD.cs.value(1)
        self.disp_drv.flush_ready()
        
        gc.collect()
        
    def __init__(self,LCD=None):
        # Init parameter
        self.LCD = LCD
        
        # Set color format
        color_format = lv.COLOR_FORMAT.RGB565
        self.pixel_size = lv.color_format_get_size(color_format)
        self.rgb565_swap_func = lv.draw_sw_rgb565_swap
        
        if not lv.is_initialized(): lv.init()

        # create event loop if not yet present
        if not lv_utils.event_loop.is_running(): event_loop=lv_utils.event_loop()

        # Init LVGL display
        self.buf1 = lv.draw_buf_create(self.LCD.width, self.LCD.height // 3, color_format, 0)
        self.buf2 = lv.draw_buf_create(self.LCD.width, self.LCD.height // 3, color_format, 0)   
        self.disp_drv = lv.display_create(self.LCD.width, self.LCD.height)
        self.disp_drv.set_color_format(color_format)
        self.disp_drv.set_draw_buffers(self.buf1, self.buf2)
        self.disp_drv.set_render_mode(lv.DISPLAY_RENDER_MODE.PARTIAL)
        self.disp_drv.set_flush_cb(self.disp_drv_flush_cb)
        
        # Init DMA
        self.dma = rp2.DMA() 








