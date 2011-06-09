"""Wrapper around withings API.

See http://www.withings.com/en/api/bodyscale .
"""
import datetime
import urllib2
import simplejson

URL = 'http://wbsapi.withings.net/measure?action=getmeas&userid=%d&publickey=%s'


class WithingsWrapper:
  TYPES = {
      1: 'weight',
      4: 'size',
      5: 'fat_free_mass',
      6: 'fat_ratio',
      8: 'fat_mass_weight',
      9: 'diastolic_blood_pressure',
      10: 'systolic_blood_pressure',
      11: 'pulse',
      }

  def _get_measurement_raw(self, id, key):
    """Get raw json for measurement."""
    url = URL % (id, key)
    content = urllib2.urlopen(url)
    json = simplejson.load(content)
    content.close()
    return json

  def get_measurements(self, id, key):
    """Yield (date, measure, value) tuple.
    """
    m = self._get_measurement_raw(id, key)
    m = m.get('body', {}).get('measuregrps', {})
    if not m:
      return

    for entry in m:
      # Category 1 is actual measure, as opposed to objective.
      # Skip all others.
      if entry['category'] != 1:
        continue
      date = datetime.datetime.fromtimestamp(entry['date'])
      for measure in entry['measures']:
        name = measure['type']
        name = self.TYPES.get(name, str(name))
        # actual value = value * 10^unit
        val = measure.get('value', 0) * (10 ** measure.get('unit', 0))
        yield date, name, val

