#!/usr/bin/env python3
"""Write the IBus component XML: one input method per layout (Avro Phonetic, Popy, every bundled fixed layout)."""
import os, sys
from xml.sax.saxutils import escape
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from avrokb import config, layouts

engines = [(config.ENGINE_PHONETIC, "Avro Phonetic", "Classic Avro phonetic typing"),
           (config.ENGINE_POPY, "Popy Layout", "Rule based Popy phonetic layout"),
           (config.ENGINE_GENERIC, "Popy Keyboard (choose layout in settings)", "Layout taken from Popy Keyboard settings")]
for lay in layouts.list_layouts([config.package_data_dir() + "/layouts"]):
    engines.append((config.FIXED_PREFIX + config.slug(lay.name), lay.name, "Fixed keyboard layout: " + lay.name))
out = ["<?xml version=\"1.0\" encoding=\"utf-8\"?>", "<component>",
       "  <name>org.freedesktop.IBus.PopyKeyboard</name>",
       "  <description>Popy Keyboard - Bangla typing</description>",
       "  <exec>/usr/lib/popy-keyboard/ibus-engine-popy --ibus</exec>",
       "  <version>1.0.0</version>", "  <author>OmicronLab and contributors</author>",
       "  <license>MPL-2.0</license>", "  <homepage>https://www.omicronlab.com</homepage>",
       "  <textdomain>popy-keyboard</textdomain>", "  <engines>"]
for name, longname, desc in engines:
    out += ["    <engine>", "      <name>%s</name>" % name, "      <language>bn</language>",
            "      <license>MPL-2.0</license>", "      <author>OmicronLab and contributors</author>",
            "      <icon>popy-keyboard</icon>", "      <layout>us</layout>",
            "      <longname>%s</longname>" % escape(longname), "      <description>%s</description>" % escape(desc),
            "      <rank>1</rank>", "      <setup>/usr/bin/popy-keyboard-settings</setup>", "    </engine>"]
out += ["  </engines>", "</component>", ""]
sys.stdout.write("\n".join(out))
