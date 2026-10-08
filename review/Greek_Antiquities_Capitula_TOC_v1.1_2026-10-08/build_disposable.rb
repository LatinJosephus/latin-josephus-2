require 'jekyll'
require 'json'
source=ARGV.fetch(0)
destination=ARGV.fetch(1)
options={'source'=>source,'destination'=>destination,'disable_disk_cache'=>true,'exclude'=>['bin','Gemfile','Gemfile.lock','vendor','review'],'quiet'=>false,'trace'=>true}
options['plugins']=Jekyll.configuration({'source'=>source})['plugins'].reject{|p| p=='jekyll-responsive-image'}
Jekyll::Commands::Build.process(options)
puts JSON.generate({'result'=>'PASS','source'=>source,'destination'=>destination,'disk_cache'=>false,'excluded_research_archive'=>true})
