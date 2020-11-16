// Code generated by "stringer -type=DesktopFirmwareType -trimprefix=DesktopFirmwareType"; DO NOT EDIT.

package model

import "strconv"

func _() {
	// An "invalid array index" compiler error signifies that the constant values have changed.
	// Re-run the stringer command to generate them again.
	var x [1]struct{}
	_ = x[DesktopFirmwareTypeUnknown-0]
	_ = x[DesktopFirmwareTypeBIOS-1]
	_ = x[DesktopFirmwareTypeEFI-2]
}

const _DesktopFirmwareType_name = "UnknownBIOSEFI"

var _DesktopFirmwareType_index = [...]uint8{0, 7, 11, 14}

func (i DesktopFirmwareType) String() string {
	if i < 0 || i >= DesktopFirmwareType(len(_DesktopFirmwareType_index)-1) {
		return "DesktopFirmwareType(" + strconv.FormatInt(int64(i), 10) + ")"
	}
	return _DesktopFirmwareType_name[_DesktopFirmwareType_index[i]:_DesktopFirmwareType_index[i+1]]
}