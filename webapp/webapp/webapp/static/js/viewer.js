/*
* Copyright 2017 the Isard-vdi project authors:
*      Josep Maria Viñolas Auquer
*      Alberto Larraz Dalmases
* License: AGPLv3
*/

function startClientVpnSocket(socket){
    $('#btn-uservpninstall').on('click', function () {
        socket.emit('vpn',{'vpn':'users','kind':'install','os':getOS()});   
    });
    $('#btn-uservpnconfig').on('click', function () {
        socket.emit('vpn',{'vpn':'users','kind':'config','os':getOS()});   
    });
    $('#btn-uservpnclient').on('click', function () {
        socket.emit('vpn',{'vpn':'users','kind':'client','os':getOS()});   
    });

    socket.on('vpn', function (data) {
        var data = JSON.parse(data);
        if(data['kind']=='url'){
            window.open(data['url'], '_blank');            
        }
        if(data['kind']=='file'){
            var vpnFile = new Blob([data['content']], {type: data['mime']});
            var a = document.createElement('a');
                a.download = data['name']+'.'+data['ext'];
                a.href = window.URL.createObjectURL(vpnFile);
            var ev = document.createEvent("MouseEvents");
                ev.initMouseEvent("click", true, false, self, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
                a.dispatchEvent(ev);              
        }
    });
}

function setViewerButtons(data,socket,offer){
    offer=[]
    if (
        ["default", "vga"].some(
            (item) => data.create_dict.hardware.videos.includes(item)
        )
    ) {
        offer.push(
            {
                'type': 'spice',
                'client': 'app',
                'secure': true,
                'preferred': true
            },{
                'type': 'vnc',
                'client': 'websocket',
                'secure': true,
                'preferred': false
            }
        )
    }
    if (
        data.os.startsWith("win")
        &&
        data.create_dict.hardware.interfaces.includes("wireguard")
    ) {
        offer.push(
            {
                'type': 'rdpvpn',
                'client': 'app',
                'secure': true,
                'preferred': false
            },{
                'type': 'rdp',
                'client': 'websocket',
                'secure': true,
                'preferred': false
            }
        )
    }
    html=""
    $.each(offer, function(idx,disp){
            prehtml='<div class="row"><div class="col-12 text-center">'
            posthtml='</div></div>'
            success='btn-round btn-info'
            preferred=''
            w='50'
            lock='<i class="fa fa-unlock"></i>'
            type=''
            btntext=''
            br=''
            if(disp['preferred']){
                success='btn-success'
                preferred='btn-lg'
                w='70'
                br='<br>'
            }
            if(disp['secure']){
                lock='<i class="fa fa-lock"></i>'
            }
            if(disp['client']=='app'){
                type='<i class="fa fa-download"></i>'
                btntext=disp['type'].toUpperCase()+' Application'
                client='file'
            }
            else if(disp['client']=='websocket'){
                type='<i class="fa fa-html5"></i>'
                btntext=disp['type'].toUpperCase()+' Browser'
                client='browser'
            }
            html=br+html+prehtml+'<button data-pk="'+data.id+'" data-type="'+disp['type']+'" data-client="'+client+'" data-os="'+getOS()+'" type="button" class="btn '+success+' '+preferred+' btn-viewers" style="width:'+w+'%">'+lock+' '+type+' '+btntext+'</button>'+posthtml+br
    })
    if (data.create_dict.hardware.interfaces.includes("wireguard")) {
        html+=prehtml+'<div id="vpn-ip" style="width:50% height:2000px"><i class="fa fa-lock"></i> <i class="fa fa-link"></i> Desktop IP (via VPN): </div>'+posthtml
    }
    $('#viewer-buttons').html(html);
    loading='<i class="fa fa-spinner fa-pulse fa-1x fa-fw"></i>'
    $('#viewer-buttons button[data-type^="rdp"]').prop("disabled", true).append(loading);
    $('#vpn-ip').append(loading);
    $('#viewer-buttons .btn-viewers').on('click', function () {
        if($('#chk-viewers').iCheck('update')[0].checked){
            preferred=true
        }else{
            preferred=false
        }
        console.log($(this).data('type')+'-'+$(this).data('client'))
        $.ajax({
            type: "GET",
            url:"/api/v3/desktop/" + $(this).data('pk') + "/viewer/" + $(this).data('client') + "-" + $(this).data('type'),
            success: function (data) {
                var el = document.createElement('a')
                if (data.kind === 'file') {
                    el.setAttribute(
                        'href',
                        `data:${data.mime};charset=utf-8,${encodeURIComponent(data.content)}`
                    )
                    el.setAttribute('download', `${data.name}.${data.ext}`)
                } else if (data.kind === 'browser') {
                    setCookie('browser_viewer', data.cookie)
                    el.setAttribute('href', data.viewer)
                    el.setAttribute('target', '_blank')
                }
                el.style.display = 'none'
                document.body.appendChild(el)
                el.click()
                document.body.removeChild(el)
            }
        })
        $("#modalOpenViewer").modal('hide');        
    });
}

function viewerButtonsIP(ip){
    $('#vpn-ip').html('<i class="fa fa-lock"></i> <i class="fa fa-link"></i> Desktop IP (via vpn): '+ip)
    $('#vpn-ip i.fa-spinner').remove()
    $('#viewer-buttons button[data-type^="rdp"]').prop("disabled", false)
    $('#viewer-buttons button[data-type^="rdp"] i.fa-spinner').remove()
}

function setCookie(name,value,days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}


function setViewerHelp(){
    $(".howto-"+getOS()).css("display", "block");
}

function getOS() {
      var userAgent = window.navigator.userAgent,
          platform = window.navigator.platform,
          macosPlatforms = ['Macintosh', 'MacIntel', 'MacPPC', 'Mac68K'],
          windowsPlatforms = ['Win32', 'Win64', 'Windows', 'WinCE'],
          iosPlatforms = ['iPhone', 'iPad', 'iPod'],
          os = null;
      if (macosPlatforms.indexOf(platform) !== -1) {
        os = 'MacOS';
      } else if (iosPlatforms.indexOf(platform) !== -1) {
        os = 'iOS';
      } else if (windowsPlatforms.indexOf(platform) !== -1) {
        os = 'Windows';
      } else if (/Android/.test(userAgent)) {
        os = 'Android';
      } else if (!os && /Linux/.test(platform)) {
        os = 'Linux';
      }
      return os;
}
