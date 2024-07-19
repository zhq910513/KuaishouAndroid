// sig     com.yxcorp.gifshow.retrofit.k
Java.perform(function(){
    console.warn("*** Start Hook ***")

    var hookSig = Java.use('com.yxcorp.gifshow.retrofit.k');
    hookSig.computeSignature.implementation = function(arr1, arr2, arr3){
        console.error("************* arr1 传入值 *************")
        console.log(arr1)

        console.error("************* arr1  url值 *************")
        var Request = Java.use('okhttp3.Request');
        var Java_Request = Java.cast(arr1, Request);
        console.log(Java_Request.url())

        var Map = Java.use('java.util.HashMap');
        console.error("************* args_map_2 传入值 *************")
        var args_map_2 = Java.cast(arr2, Map);
        console.log(args_map_2.toString())

        console.error("************* args_map_3 传入值 *************")
        var args_map_3 = Java.cast(arr3, Map);
        console.log(args_map_3.toString())

        var return_sig = this.computeSignature(arr1, arr2, arr3);
        console.error("******************************************************************************")
        console.log(Java_Request.url())
        console.error("************* args_map_2 传入值 *************")
        console.log(args_map_2.toString())
        console.error("************* args_map_3 传入值 *************")
        console.log(args_map_3.toString())
        console.error("************* user/profile/v2 ---- sig 返回值 *************")
        console.log(return_sig)
        console.error("******************************************************************************")
        return return_sig;
    }
})

// __NStokensig     com.yxcorp.gifshow.retrofit.k
Java.perform(function(){
    console.warn("*** Start Hook ***")

    var hookNS = Java.use('com.yxcorp.gifshow.retrofit.k');
    hookNS.computeTokenSignature.implementation = function(str1, str2){
        console.error("******************************************************************************")
        console.error("************* str1 传入值 *************")
        console.log(str1)

        console.error("************* str2 传入值 ClientSalt *************")
        console.log(str2)

        var return_ns = this.computeTokenSignature(str1, str2);
        console.error("************* user/profile/v2 ---- __NStokensig 返回值 *************")
        console.log(return_ns)
        console.error("******************************************************************************")

        return return_ns;
    }
})