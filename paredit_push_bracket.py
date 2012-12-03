import sublime, sublime_plugin

class PareditPushBracketCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    for region in self.view.sel():
      # Find the first closing bracket
      openings = 0
      quit = 0
      pos = self.view.sel()[0].begin()
      while True:
        next_opening = self.view.find('\(', pos)
        next_closing = self.view.find('\)', pos)
        if (next_opening != None) and ( next_opening.begin() < next_closing.begin()):
          openings += 1
          pos = next_closing.begin()+1
        elif next_closing == None:
          first_closing = self.view.line(region).end()
          print 'first break'
          break
        elif (next_opening == None) or ( next_opening.begin() > next_closing.begin()):
          first_closing = next_closing
          print "FOUND first_closing at "+ str(first_closing)
          print "FOUND next_opening at "+ str(next_opening)
          break
        else:
          pos = next_closing.begin()+1
          quit += 1
          if (quit > 6):
            print '\nbreaking\n'
            break

      # Then call the recursive try_to_close function, if there's a closing bracket.
      if first_closing != None:
        print 'starting with '+str(openings)+' openings'
        quit = 0
        pos = first_closing.begin()
        
        next_opening = self.view.find('\(', pos)
        while True:
          next_closing = self.view.find('\)', pos)
          print 'next_closing is '+str(next_closing)
          if openings > 0:
            openings -= 1
            print 'openings reduced to '+str(openings)
            pos = next_closing.begin()+1
          elif next_closing == None:
            self.view.erase(edit, first_closing)
            self.view.insert(edit, self.view.line(region).end(), ')')
            break
          elif openings == 0:
            self.view.erase(edit, first_closing)
            self.view.insert(edit, self.view.find('\)',next_closing.begin()).begin()+1, ')')
            break
          else:
            if self.view.size() == pos:
              print 'Nothing to close'
              break
            else:
              pos = next_closing.begin()+1
              quit += 1
              if (quit > 6):
                print '\nbreaking\n'
                break

      else:
        print 'Nothing to close'
