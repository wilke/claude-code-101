# Workflow for Files-not-Chats with ClaudeCode 

* Starting (use 'claude --resume') or explicitly ask clause to read:
  '''
  read the MERMORY.md file to understand where we are
  read the STATUS.md file to see our current statur
  '''
* Planning mode: Press '<shift>+<tab>' twice in prompt; alternative:
  'plan: <task description>'
  + Save the new plan in plans/ directory 'YEAR-MM-DD-<stub>.md'
* Before exiting claudeCode: update MEMORY.md and overwrite STATUS.md
  '''
  summarize what we did and append a dated entry to MEMORY.md
  overwrite STATUS.md with where we are now
  '''
  
