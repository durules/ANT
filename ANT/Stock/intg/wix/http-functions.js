import { ok, badRequest, notFound, serverError } from 'wix-http-functions';
import wixData from 'wix-data';
import { getSecret } from 'wix-secrets-backend';

/*Перевод даты в строку */
function dateToStr(date) {
  if (date != null) {
    return date.toISOString()
  } else {
    return null
  }

}

function strToDate(str) {
  if (str != null) {
    return new Date(str)
  } else {
    return null
  }

}

/**
 * Получение заказов.
 * Url для запросов https://www.svaroghunt.ru/_functions/orders
 * В заголовок "secret" передается секрентный ключ с именем "svarog_manufacture"
 * Доступные параметры:
 *   order_id_array - строка вида "11794;11793" содержит номера заказов, разделенных через ";".
 *                    Позволяет получить заказы по их номерам
 *   order_create_date - строка, содрежащая дату в формате ISO, например "2021-10-18T17:50:02.719Z".
 *                       Позволяет отобрать заказы, чья дата создания больше или равна переданной
 */
export function get_orders(request) {
  let response = {
    "headers": {
      "Content-Type": "application/json"
    },
  };

  //проверка секрета

  return getSecret('svarog_manufacture')
  .then(
    storedSecret => {
      //секрет из запроса
      let requestSecret
      //перечень идентификаторов заказов в запросе
      let order_id_array
      //дата создания от
      let order_create_date

      if (request.headers) {
        requestSecret = request.headers.secret
      }

      if (!requestSecret || storedSecret.localeCompare(requestSecret) != 0) {
        response.body = {
          "error": "Не совпадает секретный ключ"
        }
        return badRequest(response)
      }

      if (request.query) {
        order_id_array = request.query.order_id_array
        order_create_date = request.query.order_create_date
      }

      let dataOptions = {
        "suppressAuth": true
      };

      response.body = {
        "date": dateToStr(new Date()),
        "query": {
          "order_id_array": order_id_array,
          "order_create_date": order_create_date
        }
      }

      let orderQuery = wixData.query("Stores/Orders")

      //фильтрация
      if (order_id_array) {
        const orderArray = order_id_array.split(";").map(Number)
        orderQuery = orderQuery.hasSome("number", orderArray)
      }
      if (order_create_date) {
        const date = strToDate(order_create_date)
        orderQuery = orderQuery.ge("_dateCreated", date)
      }

      return orderQuery
      .find(dataOptions)
      .then(results => {
          response.body.orders = results.items
          return ok(response)
      })

    }
  )
  .catch(error => {
    response.body = {
      "error": error
    }
    return serverError(response)
  })
}
