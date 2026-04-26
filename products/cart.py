class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product_id, name=None, price=None):
        product_id = str(product_id)
        if product_id not in self.cart:
            self.cart[product_id] = {'qty': 1, 'name': name, 'price': price}
        else:
            self.cart[product_id]['qty'] += 1
        self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True
