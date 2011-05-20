UI_SOURCES=$(wildcard ui/*.ui)
UI_FILES=$(patsubst %.ui,%_ui.py,$(UI_SOURCES))

GEN_FILES = ${UI_FILES} resources.py

all: $(GEN_FILES)
ui: $(UI_FILES)
resources: resources.py

$(UI_FILES): %_ui.py: %.ui
	pyuic4 -o $@ $<
	
resources.py: resources.qrc
	pyrcc4 -o resources.py resources.qrc


clean:
	rm -f $(GEN_FILES) *.pyc

package:
	cd .. && rm -f TransformationTool.zip && zip -r TransformationTool.zip TransformationTool -x \*.svn* -x \*.pyc -x \*~ -x \*entries\* -x \*.git\*
