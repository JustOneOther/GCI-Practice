# I don't really know what I'm doing, so it'll be a miracle if this works
# TTK package to implement custom themes for GCI Trainer

namespace eval ttk::theme::damsel {

	# Iterates through images and appends them to array images
	variable imgDirect
	variable images
	set imgDirect [file join [file dirname [info script]] "damsel_imgs"]
	foreach imgFile [glob -dir $imgDirect *.png] {
		variable img
		set img [file tail [file rootname $imgFile]]
		set images($img) [image create photo -file imgFile]
	}

	# Sets up array of colors
	variable colors
	array set colors {
		-bg			"#000000"
		-fg			"#ffffff"
		-disbg		"#888888"
		-disfg		"#888888"
		-selbg		"#cccccc"
		-selfg		"#333333"
		-focus		"#aaaaee"
		-window		"#eeaaaa"
	}

	# ---------- Ttk style creation and hierarchies ----------

	# Create the style
	ttk::style theme create damsel -parent default -settings{
		# Configure style stuff
		ttk::style configure . \
			-background $colors(-bg) \
			-foreground $colors(-fg) \
			-troughcolor $colors(-bg) \
			-selectbg $colors(-selbg) \
			-selectfg $colors(-selfg) \
			-fieldbg $colors(-window) \
			-font TkDefaultFont \
			-borderwidth 1 \
			-focuscolor $colors(-focus)

		ttk::style map . \
			-foreground [list disabled $colors(-disfg)]
			-background [list disabled $colors(-disbg)]

		ttk::style layout TButton {
			# TODO Continue from here, determine if above is nessecary
		}


	}
}