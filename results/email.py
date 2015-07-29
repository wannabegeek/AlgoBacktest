from io import StringIO
import smtplib
import logging
import datetime
import locale

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# me == my email address
# you == recipient's email address
import io
from results.equity_curve import MatlibPlotResults

me = "blackbox@wannabegeek.com"
you = "tom@wannabegeek.com"


locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')

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


    total_positions = len(list(filter(lambda x: not x.is_open(), container.context.positions)))

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
    start_time = container.context.start_time
    end_time = datetime.datetime.min
    for symbol_context in container.context.symbolContexts.values():
        have_quote = True
        quote = symbol_context.quotes[-1]
        end_time = max(quote.start_time + quote.period, end_time)

    if have_quote is True:
        textLog.append("Period:           %s -> %s" % (start_time.strftime("%d-%m-%Y %H:%M:%S"), end_time.strftime("%d-%m-%Y %H:%M:%S")))
        htmlLog.append("Period:           <b>%s -&gt; %s </b>" % (start_time.strftime("%d-%m-%Y %H:%M:%S"), end_time.strftime("%d-%m-%Y %H:%M:%S")))
    else:
        textLog.append("Period:           No Data")
        htmlLog.append("Period:           <b>No Data</b>")

    textLog.append("Starting Capital: %s" % (locale.currency(container.starting_capital, grouping=True),))
    textLog.append("Current Capital:  %s" % (locale.currency(container.context.working_capital, grouping=True),))
    htmlLog.append("Starting Capital: <b>%s</b>" % (locale.currency(container.starting_capital, grouping=True),))
    htmlLog.append("Current Capital:  <b style='color:#%s'>%s</b>" % ("FF0000" if container.context.working_capital < container.starting_capital else "00FF00", locale.currency(container.context.working_capital, grouping=True)))
    percent_change = ((container.context.working_capital - container.starting_capital) / container.starting_capital) * 100.0
    htmlLog.append("Change:  <b style='color:#%s'>%.2f&#37;</b>" % ("FF0000" if percent_change < 0.0 else "00FF00", percent_change))
    if total_positions == 0:
        textLog.append("No Positions taken")
    else:
        open = list(map(lambda x: "%s" % (x), filter(lambda x: x.is_open(), container.context.positions)))

        closed_positions = sorted(filter(lambda x: not x.is_open(), container.context.positions), key=lambda x: x.exit_tick.timestamp)
        winning = list(filter(lambda x: x.points_delta() > 0.0, closed_positions))

        textLog.append("Winning Ratio: %.2f%%" % ((len(winning)/total_positions * 100),))
        htmlLog.append("Winning Ratio: <b>%.2f%%</b>" % ((len(winning)/total_positions * 100),))
        textLog.append("Total Pts:     %.2f" % (sum([x.points_delta() for x in closed_positions]), ))
        htmlLog.append("Total Pts:     <b>%.2f</b>" % (sum([x.points_delta() for x in closed_positions]), ))
        textLog.append("------------------------")
        htmlLog.append("<hr/>")
        htmlLog.append("<img src='cid:image1'>")

        closed = list(map(lambda x: "%s  --> %.2fpts (%s)" % (x, x.points_delta(), x.position_time()), closed_positions))
        textLog.append("Completed:\n%s" % ("\n".join(closed),))
        closed = list(map(lambda x: "\t%s%s  --> %.2fpts (%s)</span>" % ("<span style='color:#FF0000'>" if x.points_delta() < 0.0 else "<span style='color:#00FF00'>", x, x.points_delta(), x.position_time()), closed_positions))
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

    d = MatlibPlotResults()
    buf = io.BytesIO()
    d.display(container, buf)
    buf.seek(0)
    msgImage = MIMEImage(buf.getvalue())
    msgImage.add_header('Content-ID', '<image1>')
    msg.attach(msgImage)

    # Send the message
    s = smtplib.SMTP('joshua.dreamthought.com')
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(me, you, msg.as_string())
    s.quit()

