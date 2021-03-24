import dateutil.parser
import calendar
from optparse import OptionParser
from array import array
import AaptosDb
import ROOT


def main_db(t0, t1, filename):
    # open the db
    dbstore = AaptosDb.DbStore()
    timerange = (t0, t1)
    # prepare a TTree
    f = ROOT.TFile(filename, "recreate")
    tree = ROOT.TTree("supplyReadings", "supplyReadings")
    reading_time = array("i", [0])
    instrument = array("i", [0])
    voltage = array("f", [0])
    current = array("f", [0])
    tree.Branch("reading_time", reading_time, "reading_time/I")
    tree.Branch("instrument", instrument, "instrument/I")
    tree.Branch("voltage", voltage, "voltage/F")
    tree.Branch("current", current, "current/F")
    # get readings and fill TTree
    readings = dbstore.find(
        AaptosDb.supplyReadings,
        AaptosDb.supplyReadings.reading_time > timerange[0],
        AaptosDb.supplyReadings.reading_time < timerange[1],
    )
    devices = set([reading.instrument for reading in readings])
    for index, device in enumerate(devices):
        devicereadings = readings.find(AaptosDb.supplyReadings.instrument == device)
        instrument[0] = index
        for reading in devicereadings:
            reading_time[0] = calendar.timegm(reading.reading_time.timetuple())
            voltage[0] = reading.voltage
            current[0] = reading.current
            tree.Fill()
    # write and close
    f.Write()
    f.Close()


def main():
    # options handling
    usage = """%prog [options]"""
    description = """A simple script to display voltage/current from aaptos devices.
Support for both live stream (from the SOAP server) or database inspection."""
    parser = OptionParser(usage=usage, add_help_option=True, description=description)
    parser.add_option(
        "-f",
        "--from",
        action="store",
        type="string",
        dest="beginning",
        help="beginning of the period to plot, in ISO 8601 format, YYYY-MM-DDTHH:MM:SS[.mmmmmm][+HH:MM]",
    )
    parser.add_option(
        "-t",
        "--to",
        action="store",
        type="string",
        dest="end",
        help="end of the period to plot, in ISO 8601 format, YYYY-MM-DDTHH:MM:SS[.mmmmmm][+HH:MM]",
    )
    parser.add_option(
        "-o",
        "--output",
        action="store",
        type="string",
        dest="filename",
        help="output file name",
        default="aaptos.root",
    )
    (options, args) = parser.parse_args()
    if options.beginning is None or options.end is None:
        parser.error(
            "options --from and --to are both mandatory to access the database"
        )
    try:
        initialTime = dateutil.parser.parse(options.beginning)
    except ValueError:
        parser.error("--from: unknown string format")
    try:
        finalTime = dateutil.parser.parse(options.end)
    except ValueError:
        parser.error("--from: unknown string format")
    main_db(initialTime, finalTime, options.filename)


if __name__ == "__main__":
    main()
