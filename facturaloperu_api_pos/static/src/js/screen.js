odoo.define('facturaloperu_api_pos.pos_screens', function(require) {
  "use strict";

  var screens = require('point_of_sale.screens');
  var models = require('point_of_sale.models');
  var PaymentScreenWidget = screens.PaymentScreenWidget;

  var _super_order = models.Order.prototype;

  models.PosModel.prototype.models.some(function (model) {
    if (model.model !== 'res.company') {
      return false;
    }
    ['street','city', 'state_id', 'province_id', 'district_id'].forEach(function (field) {
      if (model.fields.indexOf(field) == -1) {
        model.fields.push(field);
      }
    });
    return true;
  });

  models.PosModel.prototype.models.push({
    model: 'einvoice.catalog.06',
    fields: [
      'name',
      'code'
    ],
    domain:  function(self){
      return [];
    },
    context: function(self){
      return {};
    },
    loaded: function(self, doc_types){
      self.doc_types = doc_types;
    },
  });

  models.PosModel.prototype.models.push({
    model: 'pos.order.document.type',
    fields: [
      'name',
      'number',
    ],
    domain:  function(self){
      return [];
    },
    context: function(self){
      return {};
    },
    loaded: function(self, pos_doc_types){
      self.pos_doc_types = pos_doc_types;
    },
  });

  models.PosModel.prototype.models.push({
    model: 'pos.order.serial.number',
    fields: [
    'name',
    'document_type_id',
    'document_type_name',
    'document_type_number',
  ],
    domain:  function(self){
      return [];
    },
    context: function(self){
      return {};
    },
    loaded: function(self, serial_numbers){
      self.serial_numbers = serial_numbers;
    },
  });
  models.load_fields('res.partner', ['doc_number', 'catalog_06_id', 'state'])
  models.load_fields('pos.order', ['api_external_id', 'api_number_feapi', 'api_link_cdr', 'api_link_pdf', 'api_link_xml'])

  models.Order = models.Order.extend({
    initialize: function() {
      _super_order.initialize.apply(this, arguments);
      var order = this.pos.get_order();
      this.api_number_feapi = this.api_number_feapi || '';
      this.api_external_id = this.api_external_id || '';
      this.api_link_cdr = this.api_link_cdr || '';
      this.api_link_xml = this.api_link_xml || '';
      this.api_link_pdf = this.api_link_pdf || '';
      this.api_code_json = this.api_code_json || '';
      this.api_qr = this.api_qr || '';
      this.serial_number = this.serial_number || '';
      this.document_type_number = this.document_type_number || '';
      this.save_to_db();
      return this
    },
    export_as_JSON: function() {
      var json = _super_order.export_as_JSON.apply(this,arguments);
      json.api_external_id = this.api_external_id;
      json.api_number_feapi = this.api_number_feapi;
      json.api_link_cdr = this.api_link_cdr;
      json.api_link_xml = this.api_link_xml;
      json.api_link_pdf = this.api_link_pdf;
      json.api_code_json = this.api_code_json;
      json.api_qr = this.api_qr;
      return json;
    },
  });

  screens.ClientListScreenWidget.include({
    save_client_details: function(partner) {
      var self = this;
      var fields = {};
      this.$('.client-details-contents .detail').each(function(idx,el){
        fields[el.name] = el.value || false;
      });

      if (fields.vat) {
        fields.doc_number = fields.vat;
      }

      if (!fields.doc_number || !fields.catalog_06_id || !fields.vat) {
        this.gui.show_popup(
          'error',
          'Debe llenar los campos de Tipo de Documento y Número de Documento en el formulario del cliente.'
        );
        return;
      }
      this._super(partner);
    },
  });

  PaymentScreenWidget.include({
    get_document_type_number: function(serial_number_selected) {
      var document_type_number = ''
      for (var i = 0; i < this.pos.serial_numbers.length; i++) {
        var serial_number = this.pos.serial_numbers[i];
        if (serial_number.name == serial_number_selected) {
          document_type_number = serial_number.document_type_number;
          break;
        }
      }
      return document_type_number;
    },
    click_factura: function() {
      var self = this
      var order = self.pos.get_order();

      if ($(".js_boleta").hasClass("highlight")) {
        $(".js_boleta").toggleClass("highlight");
      } else if ($(".js_venta_interna").hasClass("highlight")) {
        $(".js_venta_interna").toggleClass("highlight");
      }

      if (!$(".js_factura").hasClass("highlight")) {
        order.serial_number = self.pos.config.iface_factura_serial_number[1];
        order.document_type_number = self.get_document_type_number(order.serial_number);
      } else {
        order.serial_number = '';
        order.document_type_number = '';
      }

      $(".js_factura").toggleClass("highlight");
    },
    click_boleta: function() {
      var self = this
      var order = self.pos.get_order();

      if ($(".js_factura").hasClass("highlight")) {
        $(".js_factura").toggleClass("highlight");
      } else if ($(".js_venta_interna").hasClass("highlight")) {
        $(".js_venta_interna").toggleClass("highlight");
      }

      if (!$(".js_boleta").hasClass("highlight")) {
        order.serial_number = self.pos.config.iface_boleta_serial_number[1];
        order.document_type_number = self.get_document_type_number(order.serial_number);
      } else {
        order.serial_number = '';
        order.document_type_number = '';
      }

      $(".js_boleta").toggleClass("highlight");
    },
    click_venta_interna: function() {
      var self = this
      var order = self.pos.get_order();

      if ($(".js_boleta").hasClass("highlight")) {
        $(".js_boleta").toggleClass("highlight");
      } else if ($(".js_factura").hasClass("highlight")) {
        $(".js_factura").toggleClass("highlight");
      }

      if (!$(".js_venta_interna").hasClass("highlight")) {
        order.serial_number = '';
        order.document_type_number = '';
      } else {
        order.serial_number = '';
        order.document_type_number = '';
      }

      $(".js_venta_interna").toggleClass("highlight");
    },
    renderElement: function() {
      var self = this;
      this._super();

      this.$('.js_factura').click(function(){
        self.click_factura();
      });

      this.$('.js_boleta').click(function(){
        self.click_boleta();
      });

      this.$('.js_venta_interna').click(function(){
        self.click_venta_interna();
      });
    },
    send_facturalo_request: function(url, token, data) {
      var request = $.ajax({
        url: url,
        method: "POST",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(data),
        cache: false,
        beforeSend: function(xhr) {
          xhr.setRequestHeader(
            "Authorization",
            'Bearer ' + token
          );
          xhr.setRequestHeader("Access-Control-Allow-Origin", "*");
        },
      })
      return $.when(
        request
      )
    },
    save_order_to_sync: function(data) {
      var order = this.pos.get_order();
      data.pos_reference = order.name
      data.session_id = this.pos.pos_session.id
      return $.when(
        this._rpc({
          model: 'pos.order.sync',
          method: 'create',
          args: [data],
        })
      )
    },
    order_is_valid: function(force_validation) {
      var self = this;
      var sup = this._super(force_validation);
      var order = this.pos.get_order();

      if (!sup) {
        return false;
      }

      if (!$(".js_venta_interna").hasClass("highlight")) {

        if (this.pos.config.is_facturalo_api && this.pos.config.facturalo_endpoint_state == 'success') {
          var client = order.get_client();

          // si monto es mayor a 700  || o || seleccionó factura y monto es menor a 700
          if(order.get_total_with_tax() > '700' || $(".js_factura").hasClass("highlight") && order.get_total_with_tax() < '700') {

            if (!client) {
              self.gui.show_popup('error', {
                title: 'Error',
                body:  'Debe seleccionar un cliente para avanzar con la venta.'
              });
              return false;
            }

            if (!client.catalog_06_id) {
              self.gui.show_popup('error', {
                title: 'Error',
                body:  'El cliente seleccionado no tiene el tipo de documento registrado, por favor actualice la información del cliente.'
              });
              return false;
            }

            // si seleccionó factura el cliente debe ser RUC
            if ($(".js_factura").hasClass("highlight") && client.catalog_06_id[0] != 4) {
              self.gui.show_popup('error', {
                title: 'Error',
                body:  'El cliente seleccionado no posee tipo de documento RUC, por favor actualice la información del cliente o seleccione otro en su lugar.'
              });
              return false;
            }

            if ($(".js_boleta").hasClass("highlight") && order.get_total_tax() > 700) {
              if (!client.doc_number) {
                self.gui.show_popup('error', {
                  title: 'Error',
                  body:  'El cliente seleccionado no tiene el número de documento registrado, por favor actualice la información del cliente.'
                });
                return false;
              }
            }
            var doc_type = this.pos.doc_types.filter(function(doc_type) {
              return doc_type.id == client.catalog_06_id[0]
            })[0].code

          } else {

            if (!client) {
              var client = [];
              client.name = 'anonimo';
              client.vat = '00000000';
              client.address = '011001';
              var doc_type = '1';
            } else {
              var doc_type = this.pos.doc_types.filter(function(doc_type) {
                return doc_type.id == client.catalog_06_id[0]
              })[0].code
            }

          }

          console.log(order)

          var company = this.pos.company;
          var currency = this.pos.currency;

          if (!$(".js_boleta").hasClass("highlight") && !$(".js_factura").hasClass("highlight") && !$(".js_nota_credito").hasClass("highlight") && !$(".js_nota_debito").hasClass("highlight")) {
            self.gui.show_popup('error', {
              title: 'Error',
              body:  'Debe seleccionar una opción de método de facturación.'
            });
            return false;
          }

          var document_type_number = order.document_type_number;
          // var serial_number = order.serial_number + '-' + order.sequence_number;
          var serial_number = order.serial_number + '-#';
          var now = moment();
          var order_date_formatted = now.format('YYYY-MM-DD');
          var order_time = now.format('HH:mm:ss');

          var amount_with_tax = order.get_total_with_tax();
          var total_without_tax = order.get_total_without_tax();
          var amount_tax = order.get_total_tax();

          var items = [];
          var totals_discount = 0;

          var orderLines = order.get_orderlines();

          for (var i = 0; i < orderLines.length; i++) {
            var line = orderLines[i];
            var product = line.get_product();
            var product_quantity = line.get_quantity();
            var product_taxes_total = 0.0;
            var taxDetails = line.get_tax_details();
            for(var id in taxDetails){
              product_taxes_total += taxDetails[id]; //monto total del igv
            }

            var taxes_porcentage = Math.round((((product.list_price + product_taxes_total) - product.list_price) / product.list_price) * 100) / product_quantity;
            //var amountIgv = (((product.list_price) * (taxes_porcentage)) * product_quantity) / 100;

            //total descuento por linea
            var total_discount_line = (product.list_price * line.discount) / 100;

            var total_item_value = (product.list_price * product_quantity) - total_discount_line;
            var total_sale_item = total_item_value - line.get_tax();

            /* NUEVAS FORMULAS */
            // cantidad de porcentaje total por unidad
            var monto_descuento_unidad = (product.list_price * line.discount) / 100;
            // cantidad de porcentaje de linea
            var monto_descuento_linea = monto_descuento_unidad * product_quantity;
            // totales->total_descuentos
            totals_discount = totals_discount + monto_descuento_linea;
            // precio por unidad
            var precio_unidad = product.list_price - monto_descuento_unidad;
            // total linea
            var monto_total_linea = precio_unidad * product_quantity;
            // valor unidad sin igv
            var igv_unidad = line.get_tax() / product_quantity;
            var valor_unidad = product.list_price - igv_unidad;


            items.push({
              "codigo_interno_del_producto": "P0121",
              "descripcion_detallada": product.display_name,
              "codigo_producto_de_sunat": "51121703",
              "unidad_de_medida": product.uom_id[1],
              "cantidad_de_unidades": product_quantity,
              "valor_unitario": valor_unidad,
              "codigo_de_tipo_de_precio": "01",
              "precio_de_venta_unitario_valor_referencial": product.list_price,
              "afectacion_al_igv": "10",
              "porcentaje_de_igv": line.get_taxes()[0].amount,
              "monto_de_igv": line.get_tax(),
              "descuentos":[
                {
                  "codigo": "00",
                  "descripcion": "Descuento",
                  "porcentaje": line.discount,
                  "monto": monto_descuento_linea,
                  "base": product.list_price * product_quantity
                }
              ],
              "valor_de_venta_por_item": monto_total_linea - line.get_tax(),
              "total_por_item": monto_total_linea
            })
          }

          var data = {
            "version_del_ubl": "v21",
            "serie_y_numero_correlativo": serial_number,
            "fecha_de_emision": order_date_formatted,
            "fecha_de_vencimiento": order_date_formatted,
            "hora_de_emision": order_time,
            "tipo_de_documento": document_type_number,
            "tipo_de_moneda": currency.name,
            "datos_del_emisor": {
              "codigo_del_domicilio_fiscal": "0000"
            },
            "datos_del_cliente_o_receptor": {
              "numero_de_documento": client.vat,
              "tipo_de_documento": doc_type,
              "apellidos_y_nombres_o_razon_social": client.name,
              "direccion": client.address
            },
            "totales": {
              "total_descuentos": totals_discount, //xml
              "total_operaciones_gravadas": total_without_tax,
              "sumatoria_igv": amount_tax,
              "total_de_la_venta": amount_with_tax,
            },
            "items": items,
            "informacion_adicional": {
              "tipo_de_operacion": "0101",
              "leyendas": []
            },
            "extras": {
              "forma_de_pago": "Efectivo",
              "observaciones": ""
            }
          }

          console.log(data)

          var url = this.pos.config.iface_facturalo_url_endpoint;
          var token = this.pos.config.iface_facturalo_token;
          var def = $.Deferred();
          var json = data;

          this.send_facturalo_request(url, token, data)
            .done(function(data) {
              var data_response = {
                api_number_feapi: data['data']['number'],
                api_external_id: data['data']['external_id'],
                api_link_cdr: data['data']['link_cdr'],
                api_link_xml: data['data']['link_xml'],
                api_link_pdf: data['data']['link_pdf'],
                api_qr: data['data']['qr'],
              }

              var domain = [['pos_reference', '=', order.name], ['session_id', '=', self.pos.pos_session.id]];
              setTimeout(function() {
                self._rpc({
                  model: 'pos.order',
                  method: 'search_read',
                  domain: domain,
                  fields: ['id'],
                }).done(function(o) {

                  if (o.length == 0) {
                    self.save_order_to_sync(data_response)
                    def.reject()
                  } else {
                    self._rpc({
                      model: 'pos.order',
                      method: 'write',
                      args: [[o[0].id], data_response],
                    }).done(function() {
                      def.resolve()
                    }).fail(function(err) {
                      self.save_order_to_sync(data_response)
                      new Noty({
                        theme: 'bootstrap-v4',
                        type: 'warning',
                        timeout: 10000,
                        layout: 'bottomRight',
                        text: '<h3>La operación ha sido registrada con algunos incovenientes en el pedido, para actualizar el pedido debe dirigirse al módulo de punto de venta e ingresar en el menú «Pedidos por sincronizar» y ejecutar las acciones pertinentes.</h3>'
                      }).show();
                      def.reject()
                    })

                    //guardo el json
                    var data_json = {
                      api_code_json: JSON.stringify(json, null, ' ')
                    }
                    self._rpc({
                      model: 'pos.order',
                      method: 'write',
                      args: [[o[0].id], data_json],
                    }).done(function() {
                      def.resolve()
                    }).fail(function(err) {
                      new Noty({
                        theme: 'bootstrap-v4',
                        type: 'warning',
                        timeout: 10000,
                        layout: 'bottomRight',
                        text: '<h3>No se ha almacenado el archivo Json generado para el envio hacia la API</h3>'
                      }).show();
                      def.reject()
                    })
                  }

                }).fail(function(err) {
                  self.save_order_to_sync(data_response)
                  new Noty({
                    theme: 'bootstrap-v4',
                    type: 'warning',
                    timeout: 10000,
                    layout: 'bottomRight',
                    text: '<h3>La operación ha sido registrada con algunos incovenientes en el pedido, para actualizar el pedido debe dirigirse al módulo de punto de venta e ingresar en el menú «Pedidos por sincronizar» y ejecutar las acciones pertinentes.</h3>'
                  }).show();
                  def.reject()
                })

              }, 3000);

              new Noty({
                theme: 'bootstrap-v4',
                type: 'success',
                timeout: 3000,
                layout: 'bottomRight',
                text: '<h3>La operación ha finalizado.</h3>'
              }).show();


              if (data['data']['number'].charAt(0) == 'B') {
                $('#receipt-type').append('BOLETA ELECTRÓNICA')
              } else {
                $('#receipt-type').append('FACTURA ELECTRÓNICA')
              }

              $('#receipt-serie-number').append(data['data']['number'])

              $('#number-to-letter').append(data['data']['number_to_letter'])

              $('#hash').append(data['data']['hash'])

              var urlcorta = url.indexOf('/api');
              var newUrl = url.substring(0, urlcorta+1) + 'search';

              $('#search').html(newUrl)

              $('#qr').html(
                '<img style="margin-top:15px;" class="qr_code" src="data:image/png;base64, ' + data['data']['qr'] + '" />'
              )

              $('#logo').html(
                '<img style="margin-top:15px;" src="' + order['pos']['company_logo']['currentSrc'] + '" />'
              )

              var typedoc = ''
              if (order['attributes']['client'] !== null) {
                if (order['attributes']['client']['catalog_06_id'][0] == 1) {
                  typedoc = 'DOC.TRIB.NO.DOM.SIN.RUC';
                } else if (order['attributes']['client']['catalog_06_id'][0] == 2) {
                  typedoc = 'DNI';
                }else if (order['attributes']['client']['catalog_06_id'][0] == 3) {
                  typedoc = 'Carnet de Extrangería';
                }else if (order['attributes']['client']['catalog_06_id'][0] == 4) {
                  typedoc = 'RUC';
                }else if (order['attributes']['client']['catalog_06_id'][0] == 5) {
                  typedoc = 'Pasaporte';
                }else if (order['attributes']['client']['catalog_06_id'][0] == 6) {
                  typedoc = 'Cédula Diplomática de Identidad';
                }else if (order['attributes']['client']['catalog_06_id'][0] == 7) {
                  typedoc = 'Varios';
                } else {
                  typedoc = '';
                }
              }

              $('#client-doc-type').append(typedoc)


            }).fail(function(xhr, status, error) {
              def.reject()
              var err = eval("(" + xhr.responseText + ")");
              self.gui.show_popup('error', {
                title: 'ERROR: Ha ocurrido un error en el envío',
                body: err.message,
              });
              return false;
            })
        };
      };
      return true;
    },
  });
});
