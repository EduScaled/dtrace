import csv
import logging
from django.utils import timezone
from celery import task
from isle.models import Event, CSVDump, Activity, Context
from isle.utils import EventGroupMaterialsCSV, BytesCsvObjWriter


@task
def generate_events_csv(dump_id, event_ids, meta):
    CSVDump.objects.filter(id=dump_id).update(status=CSVDump.STATUS_IN_PROGRESS)
    events = Event.objects.filter(id__in=event_ids).order_by('id')
    try:
        if meta['activity']:
            meta['activity'] = Activity.objects.get(id=meta['activity'])
        if meta['context']:
            meta['context'] = Context.objects.get(id=meta['context'])
        obj = EventGroupMaterialsCSV(events, meta)
        b = BytesCsvObjWriter()
        c = csv.writer(b, delimiter=';')
        for line in obj.generate():
            c.writerow(list(map(str, line)))
        csv_dump = CSVDump.objects.get(id=dump_id)
        csv_dump.csv_file.save('', content=b.file)
        csv_dump.datetime_ready = timezone.now()
        csv_dump.status = CSVDump.STATUS_COMPLETE
        csv_dump.save()
    except Exception:
        logging.exception('Failed to generate events csv')
        CSVDump.objects.filter(id=dump_id).update(status=CSVDump.STATUS_ERROR)
