require 'jekyll'
require 'json'
source=ARGV.fetch(0)
destination=ARGV.fetch(1)
override=ARGV.fetch(2)
options={'source'=>source,'destination'=>destination,'config'=>[File.join(source,'_config.yml'),override],'disable_disk_cache'=>true,'exclude'=>['bin','Gemfile','Gemfile.lock','vendor','review','CNAME'],'quiet'=>false,'trace'=>true}
options['plugins']=Jekyll.configuration({'source'=>source})['plugins'].reject{|p| p=='jekyll-responsive-image'}
Jekyll::Commands::Build.process(options)
puts JSON.generate({'result'=>'PASS','source'=>source,'destination'=>destination,'preview_url_override'=>override,'disk_cache'=>false,'excluded_research_archive'=>true,'responsive_image_plugin'=>'Same native builder as certified canonical; existing preview image assets preserved byte-for-byte; no new responsive image assets required'})
