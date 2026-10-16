# Copyright 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2018 Fabien Bourgeois <fabien@yaltik.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def set_sale_price_on_variant(env, template_id=None):
    sql = """
        UPDATE product_product pp
        SET fix_price = pt.list_price + (
            SELECT COALESCE(SUM(ptav.price_extra), 0)
            FROM product_variant_combination pvc
            LEFT JOIN product_template_attribute_value ptav ON
                ptav.id = pvc.product_template_attribute_value_id
            WHERE pvc.product_product_id = pp.id
            AND ptav.product_tmpl_id = pt.id
        )
        FROM product_template pt
        WHERE pt.id = pp.product_tmpl_id
    """
    if template_id:
        sql += "AND pt.id = %s"
        env.cr.execute(sql, (template_id,))
    else:
        env.cr.execute(sql)
    # lst_price is stored since 20.0: recompute it from the new fix_price
    domain = [("product_tmpl_id", "=", template_id)] if template_id else []
    products = env["product.product"].with_context(active_test=False).search(domain)
    products.invalidate_recordset(["fix_price"])
    env.add_to_compute(products._fields["lst_price"], products)
    products._recompute_recordset(["lst_price"])
