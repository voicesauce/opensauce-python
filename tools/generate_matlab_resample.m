% Script to generate Matlab resampled data for testing purposes

% Licensed under Apache vs (see LICENSE)

% Insert name of directory with wav files
wav_dir = '/wav-file-dir';
% Insert name of directory with wav files
wav_files = dir('/wav-file-dir/*.wav');

for i=1:length(wav_files)
    [y, Fs, nbits] = func_readwav(fullfile(wav_dir, wav_files(i).name));
    y_rs = resample(y, 16000, Fs);
    save(strcat(wav_files(i).name(1:end-4), '.mat'), 'y_rs');
end
