
function run(name) {

tag = name.replace(/\s+/g, '').replace(/\./g,'').replace(/-/g, '').replace(/\'/g, '');
tag = tag
tag = tag.toLowerCase()
$(function(){
        var feed = new Instafeed({
            get: 'tagged',
            tagName: tag,
            clientId: 'bcd816efac8548f0a76c300d2ffd7005',
            limit: 6,
            error: function(string){
                $("#instafeed").append('<img id="default-instagram-background">');
            },
            resolution: 'standard_resolution',
            template: '<a href="{{image}}"><img src="{{image}}" /></a>',



        });
            feed.run();
    });

}