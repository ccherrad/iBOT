      window.fbAsyncInit = function() {
        FB.init({
          appId      : '2411859792223785',
          cookie     : true,
          xfbml      : true,
          status     : true, 
          version    : 'v4.0'
        });
      
      FB.AppEvents.logPageView();   
      };

      function checkLoginState(){
        FB.getLoginStatus(function(response) {
          statusChangeCallback(response);
        });
      }

      function statusChangeCallback(response){
        if (response['status'] === 'connected'){

                const status = response['status']
                const token = response['authResponse']['accessToken']
                const user = response['authResponse']['userID']

                var data = {"status":status,"accessToken" : token , "user": user}

                $.ajax({
                url:"/fb-webhook-hundler/add-pages",
                type: "POST",
                data: data,
                success:function(response){location.reload(true)},
                complete:function(){},
                error:function (xhr, textStatus, thrownError){
                alert("Internal Server Error");
                }
                        });

        } 
      }

      (function(d, s, id){
        var js, fjs = d.getElementsByTagName(s)[0];
        if (d.getElementById(id)) {return;}
        js = d.createElement(s); js.id = id;
        js.src = "https://connect.facebook.net/en_US/sdk.js";
        fjs.parentNode.insertBefore(js, fjs);
      }(document, 'script', 'facebook-jssdk'));
