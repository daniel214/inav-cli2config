# iNav Target Configuration Helper Script

This script works with iNav (version 2.2 as of writing), and can be used
to interpret a command-line settings dump from the drone and convert it
to C-style code for use in target/YOUR_TARGET/config.c
This script uses settings.yaml located in the src/main/fc directory to
translate from CLI names to source code names.

The output is not guaranteed to compile and may need some hand-holding
to work properly. This is intended to save a huge amount of time in looking
up configuration struct names.

## Usage
```
~$ ./cli2config.py -h
usage: cli2config.py [-h] [-inyaml SETTINGS.YAML] [-c] [-t TABSIZE]
                     [-s START_COL] [--force-spaces]
                     infile outfile

This script converts 'set settingname = value' lines from iNav CLI dumps into
C commands that can be inserted into a target's config.c file.

positional arguments:
  infile                input text dump from CLI
  outfile               C command output file

optional arguments:
  -h, --help            show this help message and exit
  -inyaml SETTINGS.YAML
                        settings.yaml file. Looks in current directory by
                        default.
  -c, --comments        adds the cli command string as a comment in output
  -t TABSIZE, --tabsize TABSIZE
                        sets tab size (default is 8)
  -s START_COL, --start-col START_COL
                        column location to start comments if possible. Make
                        sure this is a multiple of --tabsize
  --force-spaces        forces spaces to be used instead of tabs

This is intended to help iNav hardware target developers create custom default
setups. YOUR MILEAGE MAY VARY -- this is not guaranteed to produce correct
code, but to save time chasing down config value names. Currently it does not
handle any other dump commands besides 'set'.
```
## Input Cli Dump
```
CLI

# dump
# INAV/YOUR_TARGET 2.1.0 May  6 2019 / 00:04:57 (5f5aa57)
# GCC-7.3.1 20180622 (release) [ARM/embedded-7-branch revision 261907]

mmix reset

mmix 0  1.000 -1.000  1.000 -1.000
mmix 1  1.000 -1.000 -1.000  1.000
mmix 2  1.000  1.000  1.000  1.000
mmix 3  1.000  1.000 -1.000 -1.000
smix reset

servo 0 1000 2000 1500 100
servo 1 1000 2000 1500 100
servo 2 1000 2000 1500 100
servo 3 1000 2000 1500 100
servo 4 1000 2000 1500 100
servo 5 1000 2000 1500 100
servo 6 1000 2000 1500 100
servo 7 1000 2000 1500 100
feature -THR_VBAT_COMP
feature -VBAT
feature -TX_PROF_SEL
feature -BAT_PROF_AUTOSWITCH
feature -MOTOR_STOP
.
.
.
set looptime = 1000
set gyro_sync = ON
set align_gyro = DEFAULT
set gyro_hardware_lpf = 42HZ
set gyro_lpf_hz = 60
set moron_threshold = 32
set gyro_notch1_hz = 0
set gyro_notch1_cutoff = 1
set gyro_notch2_hz = 0
set gyro_notch2_cutoff = 1
set gyro_stage2_lowpass_hz = 0
set vbat_adc_channel = 1
set rssi_adc_channel = 3
set current_adc_channel = 2
set airspeed_adc_channel = 0
set acc_notch_hz = 0
set acc_notch_cutoff = 1
set align_acc = DEFAULT
set acc_hardware = MPU6000
set acc_lpf_hz = 15
set acczero_x = 45
set acczero_y = -25
set acczero_z = -174
set accgain_x = 4097
set accgain_y = 4102
set accgain_z = 4034
set rangefinder_hardware = BENEWAKE
set rangefinder_median_filter = OFF
set opflow_hardware = MSP
set opflow_scale =  1.000
set align_opflow = CW0
.
.
.
```
## Command
`~$ ./cli2config.py cli_dump2.txt outfile.txt  -s 64 -c -t 8`

(Remember to `sudo chmod +x cli2config.py` if you want to use it this way)

## Sample Output
```cpp
gyroConfigMutable()->gyroSync = true;				// set gyro_sync = ON
gyroConfigMutable()->gyro_align = DEFAULT;			// set align_gyro = DEFAULT
gyroConfigMutable()->gyro_lpf = 42HZ;				// set gyro_hardware_lpf = 42HZ
gyroConfigMutable()->gyro_soft_lpf_hz = 60;			// set gyro_lpf_hz = 60
gyroConfigMutable()->gyroMovementCalibrationThreshold = 32;	// set moron_threshold = 32
gyroConfigMutable()->gyro_soft_notch_hz_1 = 0;			// set gyro_notch1_hz = 0
gyroConfigMutable()->gyro_soft_notch_cutoff_1 = 1;		// set gyro_notch1_cutoff = 1
gyroConfigMutable()->gyro_soft_notch_hz_2 = 0;			// set gyro_notch2_hz = 0
gyroConfigMutable()->gyro_soft_notch_cutoff_2 = 1;		// set gyro_notch2_cutoff = 1
gyroConfigMutable()->gyro_stage2_lowpass_hz = 0;		// set gyro_stage2_lowpass_hz = 0
adcChannelConfigMutable()->adcFunctionChannel[ADC_BATTERY] = 1;	// set vbat_adc_channel = 1
adcChannelConfigMutable()->adcFunctionChannel[ADC_RSSI] = 3;	// set rssi_adc_channel = 3
adcChannelConfigMutable()->adcFunctionChannel[ADC_CURRENT] = 2;	// set current_adc_channel = 2
adcChannelConfigMutable()->adcFunctionChannel[ADC_AIRSPEED] = 0;// set airspeed_adc_channel = 0
accelerometerConfigMutable()->acc_align = DEFAULT;		// set align_acc = DEFAULT
accelerometerConfigMutable()->accZero.raw[X] = 45;		// set acczero_x = 45
accelerometerConfigMutable()->accZero.raw[Y] = -25;		// set acczero_y = -25
accelerometerConfigMutable()->accZero.raw[Z] = -174;		// set acczero_z = -174
accelerometerConfigMutable()->accGain.raw[X] = 4097;		// set accgain_x = 4097
accelerometerConfigMutable()->accGain.raw[Y] = 4102;		// set accgain_y = 4102
accelerometerConfigMutable()->accGain.raw[Z] = 4034;		// set accgain_z = 4034
rangefinderConfigMutable()->use_median_filtering = false;	// set rangefinder_median_filter = OFF
opticalFlowConfigMutable()->opflow_align = CW0;			// set align_opflow = CW0
.
.
.
```

## Known Limitations
- `set looptime = 1000` is not handled because of missing information in the settings.yaml file. There may be other settings with this issue as well.
- Only `set` commands are interpreted
- Some questionable constants may be used-- this script generally assumes that non-numeric setting labels and their named C constants are the same, but that may vary.
