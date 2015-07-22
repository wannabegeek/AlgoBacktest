import smtplib
import logging
import datetime
import locale

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# me == my email address
# you == recipient's email address
me = "blackbox@wannabegeek.com"
you = "tom@wannabegeek.com"


locale.setlocale( locale.LC_ALL, '' )

def display_results(container):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('related')
    msg['Subject'] = "Backtest Results [%s]" % (container.algo.identifier(),)
    msg['From'] = me
    msg['To'] = you

    msgAlt = MIMEMultipart('alternative')
    msg.attach(msgAlt)

    # Define the image's ID as referenced above
#    msgImage.add_header('Content-ID', '<image1>')
#    msg.attach(msgImage)


    totalPositions = len(list(filter(lambda x: not x.isOpen(), container.context.positions)))

    # Create the body of the message (a plain-text and an HTML version).
    textLog = []
    htmlLog = []
    htmlLog.append("""\
    <html>
      <head></head>
      <body>
      <span style="font-family:Courier New">
    """
    )

    textLog.append("========================")
    htmlLog.append("<hr/>")
    textLog.append("Algo:             %s" % (container.algo.identifier(),))
    htmlLog.append("Algo:             <b>%s</b>" % (container.algo.identifier(),))

    have_quote = False
    startTime = container.context.startTime
    endTime = datetime.datetime.min
    for symbol_context in container.context.symbolContexts.values():
        have_quote = True
        endTime = max(symbol_context.quotes[-1].startTime, endTime)

    if have_quote is True:
        textLog.append("Period:           %s -> %s" % (startTime.strftime("%d-%m-%Y %H:%M:%S"), endTime.strftime("%d-%m-%Y %H:%M:%S")))
        htmlLog.append("Period:           <b>%s -&gt; %s </b>" % (startTime.strftime("%d-%m-%Y %H:%M:%S"), endTime.strftime("%d-%m-%Y %H:%M:%S")))
    else:
        textLog.append("Period:           No Data")
        htmlLog.append("Period:           <b>No Data</b>")

    textLog.append("Starting Capital: %s" % (locale.currency(container.starting_capital, grouping=True),))
    textLog.append("Current Capital:  %s" % (locale.currency(container.context.working_capital, grouping=True),))
    htmlLog.append("Starting Capital: <b>%s</b>" % (locale.currency(container.starting_capital, grouping=True),))
    htmlLog.append("Current Capital:  <b style='color:#%s'>%s</b>" % ("FF0000" if container.context.working_capital < container.starting_capital else "00FF00", locale.currency(container.context.working_capital, grouping=True)))
    percent_change = ((container.context.working_capital - container.starting_capital) / container.starting_capital) * 100.0
    htmlLog.append("Change:  <b style='color:#%s'>%.2f&#37;</b>" % ("FF0000" if percent_change < 0.0 else "00FF00", percent_change))
    if totalPositions == 0:
        textLog.append("No Positions taken")
    else:
        open = list(map(lambda x: "%s" % (x), filter(lambda x: x.isOpen(), container.context.positions)))

        winning = list(filter(lambda x: x.pointsDelta() > 0.0, filter(lambda x: not x.isOpen(), container.context.positions)))

        textLog.append("Winning Ratio: %.2f%%" % ((len(winning)/totalPositions * 100),))
        htmlLog.append("Winning Ratio: <b>%.2f%%</b>" % ((len(winning)/totalPositions * 100),))
        textLog.append("Total Pts:     %.2f" % (sum([x.pointsDelta() for x in filter(lambda x: not x.isOpen(), container.context.positions)]), ))
        htmlLog.append("Total Pts:     <b>%.2f</b>" % (sum([x.pointsDelta() for x in filter(lambda x: not x.isOpen(), container.context.positions)]), ))
        textLog.append("------------------------")
        htmlLog.append("<hr/>")
        closed = list(map(lambda x: "%s  --> %.2fpts (%s)" % (x, x.pointsDelta(), x.positionTime()), filter(lambda x: not x.isOpen(), container.context.positions)))
        textLog.append("Completed:\n%s" % ("\n".join(closed),))
        closed = list(map(lambda x: "\t%s%s  --> %.2fpts (%s)</span>" % ("<span style='color:#FF0000'>" if x.pointsDelta() < 0.0 else "<span style='color:#00FF00'>", x, x.pointsDelta(), x.positionTime()), filter(lambda x: not x.isOpen(), container.context.positions)))
        htmlLog.append("Completed:<br/>%s" % ("<br/>".join(closed),))
        textLog.append("Open:\n%s" % ("\n".join(open),))
        htmlLog.append("Open:<br/>%s" % ("<br/>".join(open),))

    htmlLog.append("""\
      </span>
      </body>
    </html>
    """
    )
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText("\n".join(textLog), 'plain')
    part2 = MIMEText("<br/>".join(htmlLog), 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msgAlt.attach(part1)
    msgAlt.attach(part2)

    # This example assumes the image is in the current directory

#    fp = open('/boot/grub2/themes/system/fireworks.png', 'rb')
#    msgImage = MIMEImage(fp.read())
#    fp.close()

    # Send the message
    s = smtplib.SMTP('joshua.dreamthought.com')
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(me, you, msg.as_string())
    s.quit()

