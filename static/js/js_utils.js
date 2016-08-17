/**
 * Created by spouk on 15.01.16.
 */

SPU = {};

SPU.getter = function(obj) {
    var href = obj.getAttribute('href')
    console.log("href:", obj, obj.getAttribute('href'));
    location.href = href;
};

