///**
// * Created by spouk on 21.04.15.
// */
//
//document.onreadystatechange = function () {
//    console.log(document.readyState);
//    if (document.readyState == "complete") {
//        console.log('Document ready for work');
//        //инициализация тултипов и попов бутстрапа3 и привязка к именованым тегам
//        $('.spouk_tooltip').tooltip();
//        $('.spouk_popover').popover({
//            trigger: 'hover',
//            //{#            delay: {"show": 500, "hide": 100},#}
//            //{#            content: $('.data-content').html(),#}
//            html: true
//        });
//
//    }
//};
//
//SHOP_UTILS = {};
//
//SHOP_UTILS.radioFormchecker = function (form) {
//    console.log(form.value);
//    if (form.value == 2) {
//        document.getElementById('what').style.display = "block";
//    }
//    if (form.value == 1) {
//        document.getElementById('what').style.display = "none";
//    }
//};
//
//SHOP_UTILS.getConnector = function () {
//    //создает новый XHTTPRequest объект и возвращает его в случае успеха, или false если ошибка
//    var xhr = false;
//    try {
//        xhr = new XMLHttpRequest();
//    } catch (failed) {
//        var warning = document.createElement('div');
//        warning.id = "error_xhr";
//        warning.innerHTML = "Ошибка создания XHTTPRequest, возможно ваш браузер не поддерживает этот объект. Решение установить версию браузера более новую."
//        return false;
//    }
//    return xhr;
//};
//
//
//SHOP_UTILS.capchaUndo = function (form) {
//    var xhr = SHOP_UTILS.getConnector();
//    xhr.open('GET', '/undo_capcha', true);
//    xhr.onreadystatechange = function () {
//        document.getElementById('captcha').src = '/static/img/cap.png?' + Math.random();
//        console.log('Capcha undo now' + xhr.responseText);
//    };
//    xhr.send(null);
//};
//
//SHOP_UTILS.checkFormRegister = function (formName, session_capcha) {
//    //alert(formName.capcha.value +'   '+session_capcha);
//    var input_capcha = document.getElementById('capcha');
//    var result_validate = (formName.capcha.value == session_capcha) || false;
//    if (input_capcha && !result_validate) {
//        input_capcha.stylesheet.border = "1px solid red;";
//    }
//    console.log('Check validate form for register new user in shop ', formName.capcha.value, session_capcha);
//    return (formName.capcha.value == session_capcha) || false;
//};
//SHOP_UTILS.checkFormFeedback = function (formName, session_capcha) {
//    var input_capcha = document.getElementById('input_cap');
//
//};
//
//SHOP_UTILS.checkColor = function(check_element, id_tdname){
//    var td = document.getElementById(id_tdname);
//    if (check_element.checked){
//        td.style.backgroundColor = 'lightblue';
//    } else {
//        td.style.backgroundColor = 'white';
//    }
//
//};

/**
 * Created by spouk on 21.04.15.
 */

document.onreadystatechange = function () {
    console.log(document.readyState);
    if (document.readyState == "complete") {
        console.log('Document ready for work');
        //инициализация тултипов и попов бутстрапа3 и привязка к именованым тегам
        $('.spouk_tooltip').tooltip();
        $('.spouk_popover').popover({
            trigger: 'hover',
            //{#            delay: {"show": 500, "hide": 100},#}
            //{#            content: $('.data-content').html(),#}
            html: true
        });

    }
};

SHOP_UTILS = {};


SHOP_UTILS.getmetacontent = function (name) {
    var metas = document.getElementsByTagName('meta');

    for (i = 0; i < metas.length; i++) {
        if (metas[i].getAttribute("property") == name) {
            return metas[i].getAttribute("content");
        }
    }

    return "";
};

SHOP_UTILS.radioFormchecker = function (form) {
    console.log(form.value);
    if (form.value == 2) {
        document.getElementById('what').style.display = "block";
    }
    if (form.value == 1) {
        document.getElementById('what').style.display = "none";
    }
};

SHOP_UTILS.getConnector = function () {
    //создает новый XHTTPRequest объект и возвращает его в случае успеха, или false если ошибка
    var xhr = false;
    try {
        xhr = new XMLHttpRequest();
    } catch (failed) {
        var warning = document.createElement('div');
        warning.id = "error_xhr";
        warning.innerHTML = "Ошибка создания XHTTPRequest, возможно ваш браузер не поддерживает этот объект. Решение установить версию браузера более новую."
        return false;
    }
    return xhr;
};


SHOP_UTILS.capchaUndo = function (form) {
    var xhr = SHOP_UTILS.getConnector();
    xhr.open('GET', '/undo_capcha', true);
    xhr.onreadystatechange = function () {
        document.getElementById('captcha').src = '/static/img/cap.png?' + Math.random();
        console.log('Capcha undo now' + xhr.responseText);
    };
    xhr.send(null);
};

SHOP_UTILS.checkFormRegister = function (formName, session_capcha) {
    //alert(formName.capcha.value +'   '+session_capcha);
    var input_capcha = document.getElementById('capcha');
    var result_validate = (formName.capcha.value == session_capcha) || false;
    if (input_capcha && !result_validate) {
        input_capcha.stylesheet.border = "1px solid red;";
    }
    console.log('Check validate form for register new user in shop ', formName.capcha.value, session_capcha);
    return (formName.capcha.value == session_capcha) || false;
};
SHOP_UTILS.checkFormFeedback = function (formName, session_capcha) {
    var input_capcha = document.getElementById('input_cap');

};

SHOP_UTILS.checkColor = function (check_element, id_tdname) {
    console.log(check_element, id_tdname.id);
    var tdelement = document.getElementById(id_tdname.id);
    if (check_element.checked) {
        tdelement.style.backgroundColor = 'lightblue';
        console.log('Checked');
    } else {
        tdelement.style.backgroundColor = 'white';
        console.log('NOT Checked');
    }

};

SHOP_UTILS.changeDiscount = function (check_element, origin_discount, td_name, checkbox_name) {
    var tdname = document.getElementById(td_name.id);
    var checkbox_form = document.getElementById(checkbox_name.id);

    console.log(check_element, origin_discount, td_name, checkbox_name);
    console.log('ORIGIN DISCOUNT', origin_discount);
    console.log('TD NAME ', tdname);
    if (check_element.value != origin_discount) {
        checkbox_form.checked = true;
        console.log(td_name);
        tdname.style.backgroundColor = 'lightblue';
        console.log('Change discounts');
    }
    if (check_element.value == origin_discount) {
        checkbox_form.checked = false;
        //document.getElementById(tdname).checked = false;
        tdname.style.backgroundColor = 'white';
        console.log('NOT Checked');
    }

};

SHOP_UTILS.editRubrika = function (id_rubrika) {

    var xhr = SHOP_UTILS.getConnector();
    var csrf = document.getElementById('csrf_token').value;
    console.log(id_rubrika, csrf);
    xhr.open('POST', '/spa_admin/shop_production/rubrika?action=edit');
    xhr.setRequestHeader("X-CSRFToken", csrf);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            console.log('Server back answer ok: ', xhr.responseText);
        }
    };
    xhr.send();
};

SHOP_UTILS.deleteRow = function (rowid) {

    var row = document.getElementById(rowid);
    var table = row.parentNode;
    while (table && table.tagName != 'table')
        table = table.parentNode;
    if (!table)
        return;
    table.deleteRow(row.rowIndex);

};

SHOP_UTILS.deleteRow2 = function (rowid) {
    var row = document.getElementById(rowid);
    row.parentNode.removeChild(row);
};

/**
 *  shop: basket
 */
SHOP_UTILS.tester = function (producttoken) {
    console.log('producttoken --> ', producttoken);
    //
    //var count_goods = document.getElementById('product_count_'+producttoken);
    //var productid = document.getElementById('product_id_'+producttoken);
    //var priceid  = document.getElementById('price_id_'+producttoken);
    //console.log('COUNT_GOODS ', count_goods.value, '  PRODUCTID ', productid.value, '  PRICEID ', priceid.value);
    //console.log('COUNT_GOODS ', count_goods, '  PRODUCTID ', productid, '  PRICEID ', priceid);
};


SHOP_UTILS.basket_add = function (producttoken) {
    var xhr = SHOP_UTILS.getConnector();
    var csrf = document.getElementsByName('csrf_token').content;
    var count_goods = document.getElementById('product_count_' + producttoken).value;
    var productid = document.getElementById('product_id_' + producttoken).value;
    var priceid = document.getElementById('price_id_' + producttoken).value;
    var csrftoken = $('meta[name=csrf-token]').attr('content');
    //var info = {'countgoods': count_goods, 'productid': productid, 'priceid': priceid};
    console.log('COUNT_GOODS ', count_goods, '  PRODUCTID ', productid, '  PRICEID ', priceid);
    xhr.open('POST', '/basket/add?productid=' + productid + '&priceid=' + priceid + '&countgood=' + count_goods);
    //xhr.open('POST', '/basket/add/'+productid+'&'+priceid+'&'+count_goods);
    //xhr.open('POST', '/basket/add');
    //`X-Requested-With`
    //    header and set it to "XMLHttpRequest"
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            console.log('Server back answer ok: ', xhr.responseText);
            var answer = JSON.parse(xhr.responseText);
            console.log('ANSWER PARSE ==> ', answer);
            //    обновить данные на странице по количеству товаров и сумме заказаных товаров
            // проверить на количество товара если 0 то вывести сообщение о пустой корзине  если нет то обновить данные
            var basket_empty = document.getElementById('basket_empty_span');
            var cost = document.getElementById('producttotalcost');
            var countgood = document.getElementById('producttotalcount');
            var producttextblock = document.getElementById('product_namespad');
            var basket_empty_span = document.getElementById('basket_empty_span');
            var basket_text_block = document.getElementById('product_text_basket');

            cost.innerHTML = answer.producttotalcost;
            countgood.innerHTML = answer.producttotalcount;

            producttextblock.removeAttribute('hidden');
            basket_empty_span.setAttribute('hidden', 'hidden');
            var message;
            if (answer.producttotalcount == 1) {
                message = "товар на сумму";

            }
            if ((answer.producttotalcount > 1) && (answer.producttotalcount <= 4)) {
                message = "товара на сумму";

            }
            if (answer.producttotalcount > 4) {
                message = "товаров на сумму";

            }
            basket_text_block.innerHTML = message;

            //countgood.removeAttribute('hidden');
            //cost.removeAttribute('hidden');
            //if (answer.producttotalcount == 0) {
            //    basket_empty.innerHTML = "Корзина пуста.";
            //} else {

        }
    };
    xhr.send();

};
SHOP_UTILS.basket_adding = function (baskid, znak) {
    //изменение товара в корзине на странице корзина + -

    //создание транспорта
    var xhr = SHOP_UTILS.getConnector();
    var csrf = document.getElementsByName('csrf_token').content;
    var csrftoken = $('meta[name=csrf-token]').attr('content');
    //получение всех объектов которые надо будет изменять
    //var document.querySelectorAll(".#producttotalcost")
    var count_current = document.getElementById('product_count_' + baskid).value;
    //строка таблицы из которой забираются данные и производится перерасчет
    var name_row = 'basket_product_tr_' + baskid;
    var basket_user = 'basket_user_' + baskid;

    var origin_td;
    var sp1;
    var parentDiv;

    console.log('COUNT_CURENT == >', count_current, '  ', baskid);
    xhr.open('POST', '/basket/change?baskid=' + baskid + '&znak=' + znak + '&count_good=' + count_current);
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.onprogress = function () {
        sp1 = document.createElement("span");
        sp1.setAttribute("id", "newSpan");
        var sp1_content = document.createTextNode("обработка...");
        sp1.appendChild(sp1_content);

        var sp2 = document.getElementById(basket_user);
        parentDiv = sp2.parentNode;
        origin_td = parentDiv.replaceChild(sp1, sp2);
    };

    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            console.log('Server back answer ok: ', xhr.responseText);
            var answer = JSON.parse(xhr.responseText);
            console.log('ANSWER PARSE ==> ', answer);
            //    обновить данные на странице по количеству товаров и сумме заказаных товаров
            if (answer.remove_tr == "true") {
                var name_row = 'basket_product_tr_' + baskid;
                console.log('ROW NAME FOR DELETE ===> ', name_row);
                SHOP_UTILS.deleteRow2(name_row);
            }
            if (answer.remove_tr == "false") {
                console.log('====== FALSE REMOVE TR ', answer.remove_tr);
                sp1 = document.getElementById('newSpan');
                sp1 = parentDiv.replaceChild(origin_td, sp1);
            }
            document.getElementById('basket_product_cost_' + baskid).innerHTML = answer.natural_cost;
            document.getElementById('basket_product_ammount_' + baskid).innerHTML = answer.ammount;
            document.getElementById('product_count_' + baskid).value = answer.count_good;
            document.getElementById('producttotalcost').innerHTML = answer.producttotalcost;
            document.getElementById('producttotalcount').innerHTML = answer.producttotalcount;
            document.getElementById('producttotalcost2').innerHTML = answer.producttotalcost;
            document.getElementById('producttotalcount2').innerHTML = answer.producttotalcount;

            //document.querySelectorAll(".producttotalcost").innerHTML = answer.producttotalcost;
            //document.querySelectorAll(".producttotalcount").innerHTML = answer.producttotalcount;
        }
    };
    xhr.send();

};
SHOP_UTILS.basket_delete = function (baskid) {
    var xhr = SHOP_UTILS.getConnector();
    var csrf = document.getElementsByName('csrf_token').content;
    var csrftoken = $('meta[name=csrf-token]').attr('content');

    xhr.open('POST', '/basket/del?baskid=' + baskid);
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            console.log('Server back answer ok: ', xhr.responseText);
            var answer = JSON.parse(xhr.responseText);
            console.log('ANSWER PARSE ==> ', answer);
            //обновить данные на странице по количеству товаров и сумме заказаных товаров
            if (answer.delete) {
                var elem = 'basket_product_tr_' + baskid;
                SHOP_UTILS.deleteRow2(elem);
            }
            if (answer.producttotalcount == 0){
                console.log('WARNING TOTAL COUN == 0');
                //document.getElementById('order_send_button').setAttribute("readonly","readonly");
                document.getElementById('order_send_button').style.visibility = "hidden";
            } else {
                document.getElementById('order_send_button').style.visibility = "visible";
            }
            document.getElementById('producttotalcost').innerHTML = answer.producttotalcost;
            document.getElementById('producttotalcount').innerHTML = answer.producttotalcount;
            document.getElementById('producttotalcost2').innerHTML = answer.producttotalcost;
            document.getElementById('producttotalcount2').innerHTML = answer.producttotalcount;
        }
    };
    xhr.send();
};
/**
 *  shop: order some functions
 */

SHOP_UTILS.change_delivery = function (totalsumm, typedelivery) {
    //создание и инициализация транспорта
    var xhr = SHOP_UTILS.getConnector();
    var csrf = document.getElementsByName('csrf_token').content;
    var csrftoken = $('meta[name=csrf-token]').attr('content');

    //передача параметров транспорту
    xhr.open('POST', '/basket/order_delivery?totalsumm=' + totalsumm + '&typedelivery='+ typedelivery);
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            console.log('Server back answer ok: ', xhr.responseText);
            var answer = JSON.parse(xhr.responseText);
            console.log('ANSWER PARSE ==> ', answer);
            //обновить данные на странице по окончательной цене = полная сумма товаров  + сумма на доставку
            //if (answer.delete) {
                //var elem = 'basket_product_tr_' + baskid;
                //SHOP_UTILS.deleteRow2(elem);
            //}
            document.getElementById('cost_delivery_total').innerHTML = answer.totalsumm;
            document.getElementById('type_delivery_name').innerHTML = answer.namedelivery;
            document.getElementById('cost_delivery').innerHTML = answer.deliverysumm;
            //document.getElementById('producttotalcount2').innerHTML = answer.producttotalcount;
        }
    };
    xhr.send();


};


//SHOP_UTILS.basket_ = function () {
//
//};
//SHOP_UTILS.basket_add = function () {
//
//};
