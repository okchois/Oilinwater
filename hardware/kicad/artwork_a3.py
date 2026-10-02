"""A3 six-layer routing policy; dimensions in mm, ordinary through vias.

Signal via reduction does not apply to power, surge or thermal vias.
The routing snapshot remains the geometric source for the reviewed draft.
"""
SIGNAL_NETS = {
    'NRST','SWCLK','SWDIO','PWR_FLT','OUT1_SGOOD','OUT2_SGOOD',
    'DAC_ALARM','RS485_TX','RS485_RX','RS485_DE','DAC_MISO','DAC_MOSI',
    'DAC_SCK','DAC1_LATCH','DAC2_LATCH','DAC1_SCLK','DAC2_SCLK',
    'CDC_INT','CDC_MISO','CDC_MOSI','CDC_SCK','CS_CDC',
    'SPI_SCK','SPI_MISO','SPI_MOSI','CS_ADC','ADC_DRDY',
}
SIGNAL_VIA_DIAMETER = .30
SIGNAL_VIA_DRILL = .15
GROUND_LAYERS = ('In1.Cu','In4.Cu')
STACKUP = 'JLC06161H-2116A'
