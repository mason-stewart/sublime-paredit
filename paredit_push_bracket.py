import sublime, sublime_plugin

# This plugin needs some serious refactoring, but this is my first pass.
# Wish I wasn't awful at Python. This would have taken about 4 lines of Clojure :(
# Oh well! YOLO
class PareditPushBracketCommand(sublime_plugin.TextCommand):
  def run(self, edit):

    print '\n \n \n'+'running PareditPushBracketCommand'

    for region in self.view.sel():
      # Set pos to the cursor.
      pos = self.view.sel()[0].begin()
      # Set these two variables to prevent first_closing
      # being set more than once
      first_closing = None
      first_opening = None
      first = True

      # A recursive function for finding first_closing and
      # next_closing
      def search(openings, pos, first_opening, first_closing, first):
        print "running search("+str(pos)+")"

        # Just in case the plugin gets confused and stuck in a loop.
        # Need to refactor this for sure.
        quit = 0

        while quit < 50:
          next_opening = self.view.find('\(', pos)
          print "found next_opening at "+ str(next_opening)

          next_closing = self.view.find('\)', pos)
          print "found next_closing at "+ str(next_closing)

          # Just break if both next_opening and next_closing are None
          if (next_opening == None) and (next_closing == None):
            print 'both were None. breaking!'
            break

          # Increase opening count if next_opening is positioned before next_closing
          if (next_opening != None) and (next_opening.begin() < next_closing.begin()):
            openings += 1

            # Set the position to just after the next opening, as it's nearer the cursor
            pos = next_opening.begin()+1
            print 'found an opening. increased openings to '+str(openings)

            # Mark the first_opening for indentation purposes
            if (first_opening == None):
              first_opening = next_opening

          # Otherwise...
          else:
            # If there's no first_closing yet and either
            # A. openings is 0, or
            # B. this is the first iteration through
            # then set the first_closing to next_closing
            # and set dont_break to True to prevent breaking, even with 0 openings
            if (first_closing == None and openings == 0) or (first_closing == None and first == True):
              print 'set first_closing'
              first_closing = next_closing
              dont_break = True
            # or, do nothing, and make sure dont_break is False
            else:
              dont_break = False

            # Reduce the openings count, as the previous opening paren
            # has been closed, but make sure not to go below 0
            if openings -1 >= 0:
              openings -= 1
              print 'found a closing. decreased openings to '+str(openings)
            # if the opening count would have been reduced below 0,
            # we're inside of a nested paren structure, so again, allow
            # dont_break to be True for this iteration
            else:
              dont_break = True
              print 'found a closing. left openings alone, still set to '+str(openings)

            # Set the position to just after the next closing, as it's nearer the cursor
            pos = next_closing.begin()+1

          # Tick quit up just in case we're stuck in a loop caused by weird syntax
          quit += 1

          # Break out of the while if you can.
          if openings == 0 and dont_break == False:
            print '0 openings remaining. breaking'
            break

          # From here on out, first should be false
          first = False

        # If we broke out of the look without a first_closing, let's use
        # search() again to detect.
        if first_closing == None:
          print 'manually setting first_closing'
          first_closing = next_closing

          # call search() again, but start with 0 openings each time after the first
          openings, pos, first_closing, next_closing, next_opening, first_opening, first = search(0, pos, first_opening, first_closing, first)

        return openings, pos, first_closing, next_closing, next_opening, first_opening, first

      # call seach() for the first time, and assume that there is already one opening,
      # which is the one you're inside.
      openings, pos, first_closing, next_closing, next_opening, first_opening, first = search(1, pos, first_opening, first_closing, first)

      print "\n \nfirst_closing is "+ str(first_closing)
      print "next_closing is"+ str(next_closing)

      # print "self.view.rowcol( self.view.find('\(', first_opening.begin()).begin() )[1] is "+str(self.view.rowcol( self.view.find('\(', first_opening.begin()).begin() )[1])



      # As long as first_closing and next_closing aren't None,
      # go ahead and erase and insert them, respectively
      if (first_closing != None) and (next_closing != None):

        # Go ahead and calculate the line numbers for indention
        first_opening_row = self.view.rowcol(first_opening.begin())
        next_closing_row = self.view.rowcol(next_closing.begin())

        # erase/insert
        self.view.erase(edit, first_closing)
        self.view.insert(edit, next_closing.begin(), ')')

        # After erasing/inserting, add indentation if the next_closing
        # is on a different line that the first_opening
        if first_opening_row[0] < next_closing_row[0]:
          start_indent_at = self.view.line(first_opening).end()+1
          # print 'start_indent_at is '+str(start_indent_at)

          end_indent_at = self.view.rowcol(self.view.find('\(', first_opening.begin()).begin())[1]
          print 'end_indent_at is '+str(end_indent_at)

          end_delete_at = self.view.find('\S' ,start_indent_at).begin() - start_indent_at
          # print 'end_delete_at is '+str(end_delete_at)

          lines = self.view.lines(sublime.Region(first_opening.begin(),next_closing.begin()))[1:]
          # print 'lines '+str(lines)+' are affected'

          # print 'next_opening is '+str(next_opening)

          # Iterate through a reversed array, otherwise chopping out bits messes
          # indexing of the lines.
          for line in reversed(lines):
            line_number = self.view.rowcol(line.begin())[0]+1
            line_whitespace = self.view.find('\S' ,line.begin()).begin() - line.begin()

            print 'Line '+str(line_number)+ ' has '+str(line_whitespace)+ ' spaces at the front.'
            if line_whitespace <= end_indent_at:
              print 'inserting '+str(end_indent_at - (self.view.find('\S' ,line.begin()).begin() - line.begin()))+' spaces on line '+str(line_number)
              self.view.insert(edit, line.begin(), ' '*(end_indent_at-1))

            elif line.begin() != line.end():
              erase_whitespace = line_whitespace - end_indent_at
              print 'erasing '+ str(erase_whitespace) +' spaces from line '+str(line_number)
              erase_region = sublime.Region(line.begin(), line.begin() + (line_whitespace - end_indent_at))
              self.view.erase(edit, erase_region)

            # self.view.replace(edit, sublime.Region(line.begin(), line.begin() + end_delete_at), 'hey guys')

      else:
        print 'Nothing to move.'
