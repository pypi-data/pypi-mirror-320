/*
pyodide-mkdocs-theme
Copyleft GNU GPLv3 🄯 2024 Frédéric Zinelli

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.
If not, see <https://www.gnu.org/licenses/>.
*/


import { jsLogger } from 'jsLogger'
import { getTheme, subscribeWhenReady } from 'functools'

import _anything from 'overlord'    // Enforce dependencies/import order






// Gather color theme data and create ACE theme (once only).

const getRGBChannels=colorString=>[
    colorString.slice(1, 3), colorString.slice(3, 5), colorString.slice(5, 7),
].map(s=>parseInt(s,16));


const bodyStyles = window.getComputedStyle(document.body);
const primaryColor = bodyStyles.getPropertyValue("--md-primary-fg-color");

document.documentElement.style.setProperty(
    "--main-color", getRGBChannels(primaryColor)
);

const _slate   = document.getElementById("ace_palette").dataset.aceDarkMode;
const _default = document.getElementById("ace_palette").dataset.aceLightMode;
let [default_ace_style, customLightTheme] = _default.split("|")
let [slate_ace_style,   customDarkTheme ] = _slate.split("|")
customLightTheme ||= "default"
customDarkTheme  ||= "slate"

// Correspondance between the custom and the classic palettes
CONFIG.ACE_COLOR_THEME.customThemeDefaultKey = customLightTheme
CONFIG.ACE_COLOR_THEME.customTheme = {
    [customLightTheme]: "default",
    [customDarkTheme]:  "slate",
};

// ACE style getter
CONFIG.ACE_COLOR_THEME.aceStyle = {
    default: default_ace_style,
    slate: slate_ace_style,
};



//-----------------------------------------------------------------


/**Setup reactivity for the day/night button, repainting ACE editors.
 * NOTE: yet again, jQuery didn't work on a "change" event.
 * */
document.querySelector("[data-md-color-scheme]")
        .addEventListener("change", _=>{
          LOGGER_CONFIG.ACTIVATE && jsLogger("[Paint_ACEs]")

          const theme = getTheme();
          for(const id of CONFIG.element.allEditors){
            for (let theEditor of document.querySelectorAll(`div[id^="${ id }"]`)) {
              let editor = ace.edit(theEditor.id);
              editor.setTheme(theme);
              editor.getSession().setMode("ace/mode/python");
            }
          }
        });


;(function(){

  /**Elements in tabbed divs, that may need GUI makeup actions when the tab gets clicked on.
   * */
  const TABBED_TO_MAKE_UP_GUI = new Set()

  /**Storing all the terminals n the current page, to be able to restore any active command
   * they hold, while clicking on "tabs" tend to randomly remove them or parts of them...
   * */
  const ALL_TERMINALS = []


  // Add tabbed content manager/fixxxer (transformations to apply when tabs become visible
  // or are clicked on).
  $("div.tabbed-labels label").on('click', function(){

    // Handle the terminal crazy shit: loosing segments of the current command when clicking
    // tabs somewhere else in the page...
    for(const term of ALL_TERMINALS){
      term[1] = term[0].get_command()
      term[0].disable()
    }

    // On next tick, so that the UI is up to date (mainly : the IDE isn't hidden anymore...)
    setTimeout(_=>{
      if(TABBED_TO_MAKE_UP_GUI.size){
        for(const obj of [...TABBED_TO_MAKE_UP_GUI]){
          if(obj.isGuiCompliant || obj.makeUpYourGui()){
            TABBED_TO_MAKE_UP_GUI.delete(obj)
          }
        }
      }
      for(const [term,cmd] of ALL_TERMINALS) if(cmd) term.set_command(cmd)
    })
  })



  const TO_BUILD_CONFIG = [
    ["span[id^=auto_run_]", "PyBtn"],
    ["[id^=btn_only_]",     "PyBtn"],
    ["div[id^=term_only_]", "Terminal"],
    ...CONFIG.element.allEditors.map(id=>
      [`div[id^=global_${ id }]`, id=="editor_"?"Ide":"IdeTester", id=>id.slice('global_'.length)]
    )
  ]

  const waitForOverlord=()=>{

    if(!CONFIG.overlordIsReady){
      LOGGER_CONFIG.ACTIVATE && jsLogger('[Overlord] (waiting from subscription)')
      setTimeout(waitForOverlord, 50)
      return
    }
    LOGGER_CONFIG.ACTIVATE && jsLogger('[Overlord] - Starting subscriptions')


    const to_build = TO_BUILD_CONFIG.map(
      ([query, className, transformId]) => [$(query), className, transformId]
    )
    const some_runners = to_build.some( ([jCollection,]) => jCollection.length>0 )
    let gotSomeIdes = false

    if(some_runners){
      to_build.forEach( ([jCollection, className, transformId])=>{
        jCollection.each(function(){
          const id  = transformId ? transformId(this.id) : this.id
          const elt = new CONFIG.CLASSES_POOL[className](id)
          elt.build()
          if(elt.terminal) ALL_TERMINALS.push([elt.terminal, ''])
            gotSomeIdes ||= Boolean(elt.editor)

          // Store the runner objects that couldn't be fully initiated (GUI-wise / normally happens
          // because they are in tabs) :
          if(!elt.isGuiCompliant) TABBED_TO_MAKE_UP_GUI.add(elt)
        })
      })
    }
    if(gotSomeIdes) setTimeout(CONFIG.CLASSES_POOL.Ide.enforceAceGutterFillAfterHeightsTroubles)

    if(CONFIG.CLASSES_POOL.Qcm){                          // Building qcms only if the class is defined in the page
      subscribeWhenReady("QCM", function(){
        LOGGER_CONFIG.ACTIVATE && jsLogger('[QCM]')
        CONFIG.CLASSES_POOL.Qcm.buildQcms()
      }, {now:true, runOnly:true})
    }
  }
  waitForOverlord()

})()