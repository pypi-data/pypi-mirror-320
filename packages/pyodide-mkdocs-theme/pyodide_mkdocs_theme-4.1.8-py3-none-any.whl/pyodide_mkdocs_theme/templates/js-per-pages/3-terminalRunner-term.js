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
import {
  getSelectionText,
  sleep,
  textShortener,
  txtFormat,
  withPyodideAsyncLock,
 } from 'functools'
import { PyodideSectionsRunner } from "2-pyodideSectionsRunner-runner-pyodide"
import { RuntimeManager } from '1-runtimeManager-runtime-pyodide'






class _TerminalHandler extends PyodideSectionsRunner {

  constructor(id, callInit=true){
    super(id, false)
    this.terminal      = null     // jQuery.terminal object
    this.termWrapper   = null     // jQuery Html element
    this.termEnabled   = false    // Flag to enforce activation of the terminal (admonitions+tabbed troubles)
    this.isIsolated    = id.startsWith("term_only")
    this.cmdChunk      = ""
    this.cmdOnTheRun   = ""
    this.joinTerminalLines = false
    this.eraseCmdOnTheRunInPost = false
    if(callInit) this._init()
  }

  _init(){
    super._init()
    this.alreadyRanEnv = false    // Specific to terminals, but defined "for everyone"
  }


  /**Build a jQuery terminal and bind it to the underlying pyodide runtime.
   *
   * WARNING:  If this is an IdeEditorHandler, this.id is the id of the editor div, not
   *           the id of the terminal div ! (hence the use of the termId argument)
   * */
  build(termId=null){
    if(!termId) termId = this.id
    const jqTermId = '#' + termId

    LOGGER_CONFIG.ACTIVATE && jsLogger("[Terminal] - build " + jqTermId)

    this.runnerTerm = this.getAsyncPythonExecutor()

    const termOptions = {
      greetings: "",                            // Cancel terminal banner (welcome message),
      completionEscape: false,
      prompt: CONFIG.MSG.promptStart,
      outputLimit: this.stdoutCutOff,           // this.terminal.settings().outputLimit=value (to change dynamically)
      enabled: false,                           // GET RID OF THE DAMN AUTO-SCROLL!!!!!!
      // wrap: getWrapTerms(),                  // This also deactivate colors... FUCK THIS!
      keymap: this.getTerminalBindings(),
      completion: function (command, callback) {  // AUTO-completion
        callback(pyFuncs.pyconsole.complete(command).toJs()[0]);
      },
      mousewheel: function(){ return true },    // Seems enough to fix the "no mouse wheel" troubles on terminals
      onBlur: function(){},                     // Allow to leave the textarea, focus-wise.
    }                                           // DO NOT PUT ANY CODE INSIDE THIS !! (I don't understand what's going
                                                // on here, but  this is the only way I found to make all this work...)

    this.terminal    = $(jqTermId).terminal(this.runnerTerm, termOptions)
    this.termWrapper = this.terminal.parent()

    this.terminal.history().clear()             // Clear the history from localeStorage.

    if(CONFIG._devMode) CONFIG.terms[termId]=this.terminal

    this.addEventToRunOnce(
      this.terminal, this.ensureTerminalActivationOnClick.bind(this), true
    )
    this.termWrapper.on(
      'click', this.attemptAtResolvingTerminalUiTroubles.bind(this)
    )
    this.termWrapper.find(".stdout-wraps-btn").on(
      'click', this.swapTerminalLinesJoinerForCopies.bind(this)
    )
    this.termWrapper.find(".stdout-ctrl").on(
      'click', _=>{ this.updateStdoutCutFeedback(!this.cutFeedback) }
    )
    this.updateStdoutCutFeedback(this.cutFeedback)

    this.prefillTermIfAny()

    super.build()   // Nothing done there so far, but for consistency...
  }



  /**Update the UI button status and the inner state of cutFeedback to the given value.
   * */
  updateStdoutCutFeedback(to){
    this.data.cut_feedback = CONFIG.cutFeedback = to
    const method = to ? 'removeClass' : 'addClass'
    $(this.termWrapper).find(".stdout-x-ray-svg")[method]('py_mk_hidden')
  }



  swapTerminalLinesJoinerForCopies(){
    this.joinTerminalLines = !this.joinTerminalLines
    const method = this.joinTerminalLines ? 'removeClass' : 'addClass'
    this.termWrapper.find(".stdout-wraps-btn")[method]('deactivated')
  }


  /**Because terminals are created deactivated, add an EventListener for click to reactivate them.
   * Using the async lock so that the user cannot resume a terminal while it's running (could
   * occur on first click/run).
   *
   * - Does nothing if the terminal already got activated by other means.
   * - If a selection exists, do not enable the terminal or the selection gets lost.
   * */
  ensureTerminalActivationOnClick(){
    if(!this.termEnabled){
      if(!getSelectionText()){
        this.terminal.focus(true)
        this.terminal.enable()
      }
      this.termEnabled = true
    }
  }


  /**Transfer user's resize operations to the terminal wrapper, so that the content stays
   * confined to the wrapping div.
   * */
  terminalAutoWidthOnResize(){
    const wrapperWidth = this.termWrapper.width()
    if(wrapperWidth != this.terminal.width()){
      this.terminal.width(wrapperWidth)
    }
  }


  /**This routine tries to fix the following bugs with terminals:
   *    - The 0px width terminals on tab change (markdown: `=== "tabbed"`):
   *    - The FILL content lost when the user changed of tab anywhere in the page...
   * */
  attemptAtResolvingTerminalUiTroubles(){
    const w = this.termWrapper.css('width')
    if(w != this.terminal.css('width')){
      this.terminal.css('width', w)
    }
    const h = this.termWrapper.css('height')
    if(h != this.terminal.css('height')){
      this.terminal.css('height', h)
    }

    // NOT NEEDED ANYMORE (...?)
    // if(this.isIsolated && this.prefillTerm && !this.terminal.get_command()){
    //   this.prefillTermIfAny()
    // }
  }


  /**Routine adding the given callback on a jQuery @target click event, with an automatic
   * "unsubscription on first click" wrapping logic.
   * If @withLock is true, the routine is using the Pyodide async lock, to avoid messing
   * with the global state of the page.
   * */
  addEventToRunOnce(target, cbk, withLock=false, event='click'){
    let clickHandler = async _=>{
      target.off(event, clickHandler)
      cbk()
    }
    if(withLock){
      clickHandler = withPyodideAsyncLock('term_'+event, clickHandler)
    }
    target.on(event, clickHandler)
  }



  /**Hook returning the configuration for terminal keyboard shortcuts bindings.
   * To override in child classes when needed.
   *
   * Handled here: transfer KeyInterrupt from DOM to python runtime (note: actually
   * useless as long as no worker used!).
   * */
  getTerminalBindings(){
    return ({
      "CTRL+C": async (e) => {

        // Skip if some text is selected (=> copy!)
        let txt = getSelectionText()
        if (txt) {
          e.preventDefault()
          e.stopPropagation()
          if(this.joinTerminalLines){
            txt = txt.replace(/\n/g, '')
          }
          await navigator.clipboard.writeText(txt)
          return
        }

        let currentCmd = this.terminal.get_command();
        pyFuncs.clear_console();    // Looks like it does nothing...? :/
        this.terminal.echo(CONFIG.MSG.promptStart + currentCmd);
        this.terminal.echo(txtFormat.error("KeyboardInterrupt"));
        this.terminal.set_command("");
        this.terminal.set_prompt(CONFIG.MSG.promptStart);
      },

      "CTRL+V": async(e)=>{
        e.preventDefault()
        e.stopPropagation()

        const history  = this.terminal.history()
        const current  = this.terminal.get_command()||""
        const cmd      = await navigator.clipboard.readText()||""
        const txtLines = (current + cmd).split('\n')
        const last     = txtLines.pop() ?? ''

        for(const line of txtLines){
          history.append(line)
          await this.terminal.exec(line)
        }
        const headLine = txtLines.length ? CONFIG.MSG.promptWait : CONFIG.MSG.promptStart
        this.terminal.set_prompt(headLine)
        this.terminal.set_command(last)

        // Make sure the cursor is blinking in the terminal, at the end of the last copied line:
        this.termWrapper.find('span.cmd-cursor').css('display', 'unset')
      }
    })
  }


  getAsyncPythonExecutor(){
    throw new Error('Should be overridden in the child class.')
  }


  prefillTermIfAny(){
    if(this.prefillTerm){
      const history = this.terminal.history()
      history.append(this.prefillTerm)
      this.terminal.set_command(this.prefillTerm)
    }
  }


  setupGlobalConfig(){
    super.setupGlobalConfig()
    CONFIG.cutFeedback = this.cutFeedback
    CONFIG.termMessage = this.termFeedbackFromPyodide.bind(this)
  }


  /**When a terminal is available, display stdout and errors in it, if any.
   *
   *  @format: by default `"error"`. Formatting to use for the jQuery.terminal.
   * If @format is `null`, the @content is already formatted for the terminal and no txtFormat
   * option must be applied anymore.
   * */
  giveFeedback(content, format='error'){
    if(content){
      if(format!==null) content = txtFormat[format](content)
      this.terminalEcho(content)
    }
  }


  /**Feedback coming from pyodide, one way or another...
   * Any call reaching this method is about a content to unconditionally show in the terminal.
   *
   * If @isPrint is true, the call comes from a print statement and is a stdout redirection.
   * the child method already decided if the message must be displayed or not.
   * If @isPrint is false, the call is a direct one to terminal_message, from an author or a user,
   * and the key argument has to match the STD_KEY argument
   *
   * @throws: Error if isPrint is false and the key isn't the expected one, of if the `format`
   *          option is unknown.
   */
  termFeedbackFromPyodide(_key, msg, format, isPrint=false, newline=false){
    if(!txtFormat[format]){
      throw new Error(`Unknown formatting option: ${format}`)
    }
    msg = textShortener(msg)
    this.terminalEcho(txtFormat[format](msg), {newline})
  }


  /**Internal hook, allowing to capture all the content sent to the terminal from a parent class
   * (aka, IdeTester...).
   * WARNING: at this point, the content is already formatted with jQuery.terminal syntaxes.
   * */
  terminalEcho(content, options){
    this.terminal.echo(content, options ?? {newline:true})
  }
}












export class TerminalRunner extends _TerminalHandler {


  /**Generate the async-locked callback used to run commands typed into the terminal.
   * */
  getAsyncPythonExecutor(running=CONFIG.runningMode.cmd){
    return this.lockedRunnerWithBigFailWarningFactory(
      running,
      this.setupRuntimeTerminalCmd,
      this.runTermCommand,
      this.teardownRuntimeTerminalCmd,
    )
  }

  async applyAutoRun(){
    await this.runnerTerm(this.prefillTerm)
  }



  /**Definitions of @cmdChunk and @cmdOnThRun and general context about `PyodideConsole`:
   * ------------------------------------------------------------------------------------
   *
   *
   * All those properties, but especially @cmdChunk are trickier than they seem.
   * This is essentially because the hidden/inner PyodideConsole is actually running totally
   * independently of the jQuery.terminal object itself.
   *
   * Concretely, the PyodideConsole is handling the code itself without troubles, but anything
   * other than "just run that code" (aka, installations/imports, exclusions, ...) still has to
   * be done around the console.
   *
   * Problems arise when you need to know on the JS/Theme side if the @cmdChunk is complete or not.
   *
   * To do so, you need to send the current @cmdChunk to the PyodideConsole, and that _fucking-
   * little-bastard_ will automatically schedule the async execution of any complete instruction
   * as soon as you call `pyconsole.push(chunk)`, before you can even know it is complete or not
   * on the JS/Theme side...
   *
   *
   * On top of this, what a @cmdChunk means (brain-wise), might sometimes be quite different of
   * what a terminal might actually be sending here as argument:
   *
   * @cmdChunk: This is the string content that is passed through _WHEN THE USER HITS `Enter` in
   *           the terminal without holding Shift key_. This implies @cmdChunk could concretely
   *           be a lot of different things:
   *                - A single line command, just like you'd expect:
   *                      `a = 45+6`
   *                - A multiline command, potentially with several "commands" in it (two, here):
   *                      ```
   *                      globs = {}
   *                      def func(k):
   *                          return globs.get(k, 42)
   *                      ```
   *                - The CONTINUATION of a multiline command started earlier (here it gets messy):
   *                      Previously:   `>>> """ Starting the multi thing`
   *                      Previously:   `... continue it`
   *                      Now:          `... third line`
   *
   *                      After hitting `Enter`, @cmdChunk will be `"third line"` ONLY.
   *
   *                - Any mix of all these two last...
   * */
  async setupRuntimeTerminalCmd(cmdChunk){

    this.cmdChunk    = cmdChunk
    this.cmdOnTheRun = !this.cmdOnTheRun ? cmdChunk : this.cmdOnTheRun + '\n' + cmdChunk
    this.storeUserCodeInPython('__USER_CMD__', this.cmdOnTheRun)
    this.terminal.pause()

    let runtime
    if(!this.alreadyRanEnv){
      // If an IDE-terminal is run before the IDE itself, it must run the env/post sections.
      runtime = await this.setupRuntimeTrackingEnvRun()

    }else{
      // If env already ran before, envTerm HAS to run independently, so remove the dependency.
      runtime = new RuntimeManager(this)
      runtime.changeDependency('envTerm', 'start')  // Make envTerm runnable on its own!
    }

    await this.setupRuntime(runtime, 'envTerm')
    return runtime
  }


  async setupRuntimeTrackingEnvRun(){
    const runtime = await this.setupRuntime()
    this.alreadyRanEnv = !runtime.stopped
    return runtime
  }


  /**Specific teardown steps when using a terminal command (isolated or IDE's terminal).
   * */
  async teardownRuntimeTerminalCmd(runtime){
    try{
      await runtime.runWithCtx('postTerm')
    }finally{
      // If ever postTerm failed, post might still have to run:
      await this.teardownRuntime(runtime)
      if(this.eraseCmdOnTheRunInPost) this.cmdOnTheRun = ""
    }
  }


  /**Generic terminal teardown actions (common to isolated and IDEs' terminals)
   * */
  async teardownRuntime(runtime) {
    LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - TerminalRunner teardownRuntime")
    this.terminal.resume()
    await super.teardownRuntime(runtime)
    this.storeUserCodeInPython('__USER_CMD__', "")
  }





  /**Main command routine execution logic.
   * */
  async runTermCommand(runtime){
    LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - Terminal - start running command")

    let futureAwaited = false              // Flag to know if the future has been awaited or not, in the loop
    this.eraseCmdOnTheRunInPost = false

    if(runtime.stopped){
      LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - Terminal - Skipped!")
      this.eraseCmdOnTheRunInPost = true
      return
    }



    /**Actions to perform when a command is complete or failed.
     * */
    const done = async (future)=>{
      LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - Terminal - done step. Awaited:", futureAwaited)
      this.eraseCmdOnTheRunInPost = true

      // Future destruction cannot occur if the future didn't get awaited, so make sure it has been:
      if(!futureAwaited){
        try{ await future }
        catch(e){ // console.warn(e)    // Might fail but result is useless => sink.
        }
      }
      future.destroy()
      await sleep()                     // Enforce GUI update, going through the next tick
    }



    // DO NOT use this.cmdChunk, otherwise, `import ...` in a multiline string WILL do the import... XD
    const baseCtx = {
      code: this.cmdOnTheRun,
      section: CONFIG.runningMode.cmd,
      isEnvSection: false,
      applyExclusionsIfAny: true,
      logConfig: {
        code: this.cmdOnTheRun,
        autoAssertExtraction: false,
        purgeTrace: runtime.purgeStackTrace
      },
    }

    /**Seek for excluded imports & installations, but NOT running the actual code.
     * This has to be done before any future is fed to the PyodideConsole, otherwise it WILL
     * run that code anyway...
     * */
    await runtime.runWithCtx({
      ...baseCtx,
      kwsExclusions: false,         // Skip all usual exclusions
      methodsExclusions: false,     // Skip all usual exclusions
      runtimeExclusions: false,     // Skip all usual exclusions
      method: async ()=>{},          // Nothing to do: only check.apply imports!
    })

    if(runtime.stopped){
      // Need to "consume" any currently incomplete command here, because the user wrote
      // an invalid import, but with a valid code/syntax:
      futureAwaited  = true
      const [future] = [pyFuncs.pyconsole.push(":+42")]
      try{
        await pyFuncs.await_fut(future)
      } catch(e){}
      await done(future)
      this.terminal.set_prompt(CONFIG.MSG.promptStart)
      return
    }


    const lines = this.cmdChunk.split("\n")   // Split multiline commands (for multiline FILL)

    for (let line of lines) {
      LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - Terminal - current cmd line:", line)

      /* NOTE: putting future inside an array slightly changes the behaviors about the
         "PyodideConsole future exception was never retrieved" warnings... => might be better...
         BUT... this doesn't resolve the troubles about async scheduling in any way (I checked),
         so the overall "mostly broken" setup must be kept... */
      let [future] = [pyFuncs.pyconsole.push(line)]
      futureAwaited = false

      // Set the next line prompt beginning in the terminal (command: ">>>" or continuation:"...")
      const isIncompleteExpr = future.syntax_check=="incomplete"
      const headLine = isIncompleteExpr ? CONFIG.MSG.promptWait : CONFIG.MSG.promptStart
      this.terminal.set_prompt(headLine)

      switch (future.syntax_check) {

        case "complete":
          LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - Terminal - future complete")
          try{
            /*NOTE: Imports exclusions are extra wonky, here...

              Since the future has been "setup", the underlying PyConsole WILL execute the related
              code anyway. Awaiting it or not doesn't change the fact that the JS layer of pyodide
              will see the import and install the module (see `done`: I tried without enforcing
              awaiting the future).
              BUT: with the exclusions in place, the module won't be available to the user. Not even
              through sys.modules! (I think it is installed, but never actually imported).

              So all in all: let the installation itself occur anyway, because this avoids to have
              to run something else from outside the routine like it was the case before, which was
              also causing some kinds of problems...
            */
            await runtime.runWithCtx({
              ...baseCtx,
              code:   line,
              method: async ()=>{
                LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - Terminal - awaiting future")
                futureAwaited = true
                await pyFuncs.await_fut(future)
              },
            })

          }finally{
            await done(future)
          }
          continue

        case "incomplete":
          LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - Terminal - future incomplete")
          continue

        case "syntax-error":
          LOGGER_CONFIG.ACTIVATE && jsLogger("[CheckPoint] - Terminal - future syntax error")
          this.terminal.error(future.formatted_error.trimEnd());
          await done(future)
          return

        default:
          await done(future)
          throw new Error(`Unexpected state ${future.syntax_check}`);
      }
    }
  }
}


CONFIG.CLASSES_POOL.Terminal = TerminalRunner
