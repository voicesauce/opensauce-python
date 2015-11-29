from __future__ import division

import math

from opensauce.snack import snack_pitch

from support import TestCase, wav_fns, get_test_data

class TestSnack(TestCase):

    longMessage = True

    def test_defaults(self):
        # XXX I think these are the voicesauce defaults (vs expresses them
        # in ms, but snack expects seconds).
        f_len = 0.001
        w_len = 0.025
        for fn in wav_fns:
            # XXX I think voicesauce will optionally emit the Voice data, but I
            # don't have example output data for it, so I'm ignoring it for now.
            F0, V = snack_pitch(fn, frame_length=f_len, window_length=w_len)
            # The first samples in all of our test data yield 0.
            self.assertEqual(F0[:10], [0.0]*10)
            # The snack esps data starts in the middle of the first window,
            # but the voicesauce output data starts counting frames from 0,
            # so pad our F0 with invalid frames.
            # XXX I'm not sure why -1 seems to make the data match up better,
            # voicesauce doesn't have the -1 term.
            F0[:0] = [float('NaN')] * int(math.floor(w_len/f_len/2)-1)
            # NB: It doesn't matter which output file we use, the sF0 column is
            # the same in all of them.
            voicesauce_data = get_test_data(fn, 'sF0', 'sf0', '1ms')
            os_data = []
            vs_data = []
            for ms, fs0 in voicesauce_data:
                ms = int(ms)
                # Voicesauce rounds to three places.
                os_data.append(round(F0[ms], 3))
                vs_data.append(fs0)
            # XXX debug prints.
            for i in range(len(os_data)):
                print((i, os_data[i], voicesauce_data[i]))
            print(fn)
            for i in range(len(os_data)):
                if (abs(os_data[i] - vs_data[i]) >= 40
                       and (os_data[i]==0 or vs_data[i]==0)):
                    continue
                self.assertLess(abs(os_data[i] - vs_data[i]), 0.6, "row %s" % i)
