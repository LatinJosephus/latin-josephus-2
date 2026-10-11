# Select the installed ImageMagick 6 SDK after RubyInstaller enables its compiler.
# RMagick 4.3's Windows probe otherwise finds the compiler bundle's ImageMagick 7.
require 'mkmf'
ENV['PATH'] = 'C:/workspace/Whiston-I-XI-Integration-runtime-20261011/im6-command;C:/Program Files/ImageMagick-6.9.13-Q16;' + ENV.fetch('PATH')
