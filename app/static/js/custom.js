
function deezer_download(artist, album, title, music_id, type, add_to_playlist, create_zip) {
    console.log("data: " + music_id + ", " + artist + ", " + album + ", " + title);
    $.post(deezer_downloader_api_root + '/download',
        JSON.stringify({ type: type, music_id: parseInt(music_id), artist: artist, album: album, title: title, add_to_playlist: add_to_playlist, create_zip: create_zip}),
        function(data) {
            if(create_zip == true) {
                text = "You like being offline? You will get a zip file!";
            }
            else if(type == "album") {
                if(add_to_playlist == true) {
                    text = "Good choice! The album will be downloaded and queued to the playlist";
                } else {
                    text = "Good choice! The album will be downloaded.";
                }
            } else {
                if(add_to_playlist == true) {
                    text = "Good choice! The song will be downloaded and queued to the playlist";
                } else {
                    text = "Good choice! The song will be downloaded.";
                }
            }
            $.jGrowl(text, { life: 4000 });
            console.log(data);
    });
}


function play_preview(src) {
    $("#audio_tag").attr("src", src)[0].play();
}

$(document).ready(function() {

    if(!show_mpd_features) {
        $("#yt_download_play").hide()
        $("#spotify_download_play").hide()
        $("#deezer_download_play").hide()
    };


    function youtubedl_download(add_to_playlist) {
        $.post(deezer_downloader_api_root + '/youtubedl',
            JSON.stringify({ url: $('#youtubedl-query').val(), add_to_playlist: add_to_playlist }),
            function(data) {
                console.log(data);
                $.jGrowl("As you wish", { life: 4000 });
            });
    }
    
    
    function spotify_playlist_download(add_to_playlist, create_zip) {
        $.post(deezer_downloader_api_root + '/playlist/spotify',
            JSON.stringify({ playlist_name: $('#spotify-playlist-name').val(), 
                             playlist_url: $('#spotify-playlist-url').val(),
                             add_to_playlist: add_to_playlist,
                             create_zip: create_zip}),
            function(data) {
                console.log(data);
                $.jGrowl("As you wish", { life: 4000 });
            });
    }



    function deezer_playlist_download(add_to_playlist, create_zip) {
        $.post(deezer_downloader_api_root + '/playlist/deezer',
            JSON.stringify({ playlist_url: $('#deezer-playlist-url').val(),
                             add_to_playlist: add_to_playlist,
                             create_zip: create_zip}),
            function(data) {
                console.log(data);
                $.jGrowl("As you wish", { life: 4000 });
            });
    }
    

    function search(type) {
        deezer_load_list(type, $('#songs-albums-query').val());
    }

    function search_blog(){
				var selected_blog = $('#blog_select').val();
				console.log("BLOG Search on blog: " + selected_blog)
				var search_term = $('#filter_text').val()

        $.post(deezer_downloader_api_root + '/blog_search',
            JSON.stringify({query: search_term, blog: selected_blog }),
            function(data) {
										console.log("BLOG_search data: " + data)
                    $("#results_blogs > tbody").html("");
                    for (var i = 0; i < data.length; i++) {
			                	var propValue;
			                	for(var propName in data[i]) {
			                			propValue = data[i][propName]

			                			console.log(propName,propValue);
			                	}
												if (data[i] != null){
																draw_blog_table_entry(data[i]);
												}    
								    }
				    });
		}


    function update_blog_selector() {
        $("#blog_select").empty();
				console.log("BLOGS-selector updating")
        $.post(deezer_downloader_api_root + '/blogs',
            JSON.stringify({ }),
            function(data) {
										console.log("BLOGS-data: " + data)
										var mySelect = $('#blog_select');
								    $("#blog_select").empty();
										$.each(data['blogs'], function(val, text) {
											    mySelect.append(
												       $('<option></option>').val(val).html(text)
											    );
										});
				    });
    }

    function deezer_load_list(type, query) {
        $.post(deezer_downloader_api_root + '/search',
            JSON.stringify({ type: type, query: query }),
            function(data) {
                $("#results > tbody").html("");
                for (var i = 0; i < data.length; i++) {
                    drawTableEntry(data[i], type);
                }
        });
    }


    function download_blog_release(event){
				// if dl from deezer toggled, call download_selected_deezer_entry(event)
						// else call unlock and download from filesharing sites

		}

    function download_selected_deezer_entry(event){
				var selected_deezer = $(event.target).siblings('.deezer_select').find(":selected");
				/// TODO FILL	
				//deezer_download(artist, album, title, music_id, type, false, false) {
		}


    function draw_blog_table_entry(rowData){
				var propValue;
				for(var propName in rowData) {
						propValue = rowData[propName]

						console.log(propName,propValue);
				}
				console.log("row: " + rowData)
        var row = $("<tr>");
        $("#results_blogs").append(row); 
        row.append("<td class='pull-left'><img style='float: left' src='"+rowData.url_cover + "' width=100 height=100></img><div class='blog_entry_name'>" + rowData.name + "</div></td>");
				
				if (rowData.deezer_candidates.length != 0){
				    candidates_wrap = $("<td class='deezer_result'>")
            deezer_selector = $("<select class='deezer_select'>")

			    	for (deez_result of rowData.deezer_candidates){
			    			console.log("candidate: " + deez_result)
			    	    deezer_selector.append('<option value="' + deez_result.deezer_link + '" data-imagesrc="' + deez_result.deezer_cover + '" data-description="by ' + deez_result.deezer_artist + '">' + deez_result.deezer_album + '</option>');
			    	}
				    candidates_wrap.append('<div class="pretty p-switch p-fill"><input type="checkbox" /><div class="state p-success"><label>Download from Deezer</label></div></div>');
				    candidates_wrap.append(deezer_selector);
				    row.append(candidates_wrap);
				}else{
				    row.append("<td>None found.</td>")
				}				
        
				//row.append($("<td>" + rowData.deezer_name + "</td>"));
        row.append($('<td > <button class="btn btn-default" onclick="download_blog_release()" > <i class="fa fa-download fa-lg" title="download" ></i> </button> </td>'));


    		$(".deezer_select").ddslick({
						width:500,
						height:250
				});
		}

    function drawTableEntry(rowData, mtype) {
				var propValue;
				for(var propName in rowData) {
						propValue = rowData[propName]

						console.log(propName,propValue);
				}
				console.log("row: " + rowData)
        var row = $("<tr>");
        $("#results").append(row); 
        row.append($("<td>" + rowData.artist + "</td>"));
        row.append($("<td>" + rowData.title + "</td>"));
        
        row.append("<td><img src='"+rowData.img_url+"'> " + rowData.album + "</a></td>");
        
        if (rowData.preview_url) {
            row.append($('<td> <button class="btn btn-default" onclick="play_preview(\'' + rowData.preview_url + '\');" > <i class="fa fa-headphones fa-lg" title="listen preview in browser" ></i> </button> </td>'));
        }
        
        if (mtype == "album") {
            row.append($('<td> <button class="btn btn-default"> <i class="fa fa-list fa-lg" title="list album songs" ></i> </button> </td>').click(function() {deezer_load_list("album_track", ""+rowData.album_id + "")}));
        }
        
        if(show_mpd_features) {
        row.append($('<td> <button class="btn btn-default" onclick="deezer_download(\'' +
                     rowData.artist  + '\', \'' +
                     rowData.album  + '\', \'' +
                     rowData.title  + '\', \'' +
                     rowData.id  + '\', \''+rowData.id_type +
                     '\', true, false);" > <i class="fa fa-play-circle fa-lg" title="download and queue to mpd" ></i> </button> </td>'));
        }

        row.append($('<td> <button class="btn btn-default" onclick="deezer_download(\'' +
                   rowData.artist  + '\', \'' +
                   rowData.album  + '\', \'' +
                   rowData.title  + '\', \'' +
                   rowData.id  + '\', \''+ rowData.id_type + 
                   '\', false, false);" > <i class="fa fa-download fa-lg" title="download" ></i> </button> </td>'));

        if(rowData.id_type == "album") {
            row.append($('<td> <button class="btn btn-default" onclick="deezer_download(\'' +
                     rowData.artist  + '\', \'' +
                     rowData.album  + '\', \'' +
                     rowData.title  + '\', \'' +
                       rowData.id  + '\', \''+ rowData.id_type + 
                       '\', false, true);" > <i class="fa fa-file-archive-o fa-lg" title="download as zip file" ></i> </button> </td>'));
        }
    }

    function show_debug_log() {
        $.get(deezer_downloader_api_root + '/debug', function(data) {
            var debug_log_textarea = $("#ta-debug-log");
            debug_log_textarea.val(data.debug_msg);
            if(debug_log_textarea.length) {
                debug_log_textarea.scrollTop(debug_log_textarea[0].scrollHeight - debug_log_textarea.height());
            }
        });
    }

    function show_task_queue() {
        $.get(deezer_downloader_api_root + '/queue', function(data) {
            var queue_table = $("#task-list tbody");
            queue_table.html("");
            
            for (var i = data.length - 1; i >= 0; i--) {
								clean_args = data[i].args.replace(/&#39;/g, "").replace('{','').replace('}', '').replace('"', '').replace('True', 'Yes').replace('False', 'No').split(', ');
								var html="<tr><td>"+data[i].description+"</td>";
                html += "<td>"+data[i].media_type+"</td>";
								clean_args.forEach(item => {
												// get interesting value without key
								    value = item.split(': ')[1];
										console.log('arg! : ' + value)
										html += "<td>" + value + "</td>";
								});
								if (clean_args.length == 2){
										html += "<td>No</td>";
								}
								
                html += "<td>"+data[i].state+"</td></tr>";
                $(html).appendTo(queue_table);
                switch (data[i].state) {
                case "Downloading":
                    $("<tr><td colspan=6><progress value="+data[i].progress[0]+" max="+data[i].progress[1]+" style='width:100%'/></td></tr>").appendTo(queue_table);
                case "Failed":
                    $("<tr><td colspan=6 style='color:red'>"+data[i].exception+"</td></tr>").appendTo(queue_table);
                }
            }
            if ($("#nav-task-queue").hasClass("active")) {
                setTimeout(show_task_queue, 1000);
            }
        });
    }
				/*
    $('#myDropdown').ddslick({
				onSelected: function(selectedData){
				 //callback function: do something with selectedData;
        }   
		}); */

    $("#search_track").click(function() {
        search("track");
    });

    $("#search_album").click(function() {
        search("album");
    });
    
    $("#search_blog").click(function() {
				console.log("searching blog!");
        search_blog();
    });

    $("#yt_download").click(function() {
        youtubedl_download(false);
    });
    
    $("#yt_download_play").click(function() {
        youtubedl_download(true);
    });
    
    $("#nav-debug-log").click(function() {
        show_debug_log();
    });

    $("#nav-task-queue").click(function() {
        show_task_queue();
    });

    // BEGIN SPOTIFY
    $("#spotify_download_play").click(function() {
        spotify_playlist_download(true, false);
    });

    $("#spotify_download").click(function() {
        spotify_playlist_download(false, false);
    });

    $("#spotify_zip").click(function() {
        spotify_playlist_download(false, true);
    });
    // END SPOTIFY

    
    // BEGIN DEEZER
    $("#deezer_download_play").click(function() {
        deezer_playlist_download(true, false);
    });

    $("#deezer_download").click(function() {
        deezer_playlist_download(false, false);
    });

    $("#deezer_zip").click(function() {
        deezer_playlist_download(false, true);
    });
    // END DEEZER
    $("#nav-blogs").click(function() {
        update_blog_selector();
    });

    
    function show_tab(id_nav, id_content) {
    // nav
    console.log('show_tab called! ' + id_nav);
    $(".nav-link").removeClass("active")
    //$("#btn-show-debug").addClass("active")
    $("#" + id_nav).addClass("active")

    // content
    $(".container .tab-pane").removeClass("active show")
    //$("#youtubedl").addClass("active show")
    $("#" + id_content).addClass("active show")
    }


    var bbody = document.getElementById('body');
    bbody.onkeydown = function (event) {
        if (event.key !== undefined) {
           if (event.key === 'Enter' && event.altKey) {
               console.log("pressed Enter + ALT");
               search("album");
           }  else if (event.key === 'Enter' ) {
               console.log("pressed Enter");
               search("track");
           } else if (event.key === 'm' && event.ctrlKey) {
              console.log("pressed ctrl m");
              $("#songs-albums-query")[0].value = "";
              $("#songs-albums-query")[0].focus();
           }
           if (event.ctrlKey && event.shiftKey) {
               console.log("pressed ctrl + shift + ..");
               if(event.key === '!') {
                   id_nav = "nav-songs-albums";
                   id_content = "songs_albums";
               }
               if(event.key === '"') {
                   id_nav = "nav-youtubedl";
                   id_content = "youtubedl";
               }
               if(event.key === '§') {
                   id_nav = "nav-spotify-playlists";
                   id_content = "spotify-playlists";
               }
               if(event.key === '$') {
                   id_nav = "nav-deezer-playlists";
                   id_content = "deezer-playlists";
               }
               if(event.key === '%') {
                   id_nav = "nav-songs-albums";
                   id_content = "songs_albums";
                   window.open('/downloads/', '_blank');
               }
               if(event.key === "&") {
                   id_nav = "nav-debug-log";
                   id_content = "debug";
                   show_debug_log();
               }
               if(event.key === '/') {
                   id_nav = "nav-task-queue";
                   id_content = "queue";
               }
               if(event.key === '(') {
                   id_nav = "nav-blogs";
                   id_content = "blogs";
               }
               if(typeof id_nav !== 'undefined') {
                   show_tab(id_nav, id_content);
               }
           }
        }
            
    };
});
