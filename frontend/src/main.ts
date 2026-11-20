import { ChangeDetectorRef, Component, signal } from '@angular/core';
import { bootstrapApplication } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'stockflow-app',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
<header>
  <b>StockFlow</b>
  <form (ngSubmit)="login()">
    <input aria-label="Username" [(ngModel)]="username" name="username">
    <input aria-label="Password" type="password" [(ngModel)]="password" name="password">
    <button>Sign in</button>
    <span>{{role}}</span>
  </form>
</header>
<main>
  <h1>Operations overview</h1>
  <p>Sales and inventory management</p>
  <label>Dashboard order-status filter 
    <select aria-label="Dashboard status filter" [(ngModel)]="dashboardStatus" (change)="refresh()">
      <option value="">All statuses</option>
      <option value="draft">Draft</option>
      <option value="validated">Validated</option>
      <option value="closed">Closed</option>
    </select>
  </label>
  <div class="cards">
    <article>Customers<strong>{{stats().customers||0}}</strong></article>
    <article>Products<strong>{{stats().products||0}}</strong></article>
    <article>Orders<strong>{{stats().orders||0}}</strong></article>
    <article>Closed revenue<strong>{{stats().revenue||0|currency}}</strong></article>
  </div>
  <p role="status" aria-live="polite">{{message}}</p>
  <nav>
    <button (click)="show('products')">Products</button>
    <button (click)="show('customers')">Customers</button>
    <button (click)="show('orders')">Orders</button>
    <button *ngIf="role==='admin'" (click)="show('audit')">Audit</button>
  </nav>

  <section>
    <h2>{{section}}</h2>
    <input *ngIf="section==='products'||section==='customers'" aria-label="Search" placeholder="Search" [(ngModel)]="query" (input)="load()">

    <div *ngIf="section==='products'">
      <form (ngSubmit)="saveProduct()">
        <input placeholder="Name" [(ngModel)]="form.name" name="name" required>
        <input placeholder="SKU" [(ngModel)]="form.sku" name="sku" required>
        <input placeholder="Price" type="number" min=".01" step="0.01" [(ngModel)]="form.price" name="price" required>
        <input placeholder="Stock" type="number" min="0" [(ngModel)]="form.stock" name="stock" required>
        <button [disabled]="role==='viewer'">{{editing?'Update':'Add'}} product</button>
        <button type="button" *ngIf="editing" (click)="reset()">Cancel</button>
      </form>
      <table>
        <tr><th>Name</th><th>SKU</th><th>Price</th><th>Stock</th><th></th></tr>
        <tr *ngFor="let x of rows()">
          <td>{{x.name}}</td>
          <td>{{x.sku}}</td>
          <td>{{x.price|currency}}</td>
          <td>{{x.stock}}</td>
          <td>
            <button (click)="edit(x)">Edit</button> 
            <button *ngIf="role==='admin'" (click)="remove(x.id)">Delete</button>
          </td>
        </tr>
      </table>
    </div>

    <div *ngIf="section==='customers'">
      <form (ngSubmit)="saveCustomer()">
        <input placeholder="Name" [(ngModel)]="form.name" name="name" required>
        <input placeholder="Email" type="email" [(ngModel)]="form.email" name="email" required>
        <button [disabled]="role==='viewer'">{{editing?'Update':'Add'}} customer</button>
        <button type="button" *ngIf="editing" (click)="reset()">Cancel</button>
      </form>
      <table>
        <tr><th>Name</th><th>Email</th><th></th></tr>
        <tr *ngFor="let x of rows()">
          <td>{{x.name}}</td>
          <td>{{x.email}}</td>
          <td>
            <button (click)="edit(x)">Edit</button> 
            <button *ngIf="role==='admin'" (click)="remove(x.id)">Delete</button>
          </td>
        </tr>
      </table>
    </div>

    <div *ngIf="section==='orders'">
      <p>{{customers().length}} customers, {{products().length}} products available</p>
      <form (ngSubmit)="createOrder()">
        <select aria-label="Customer" [(ngModel)]="order.customer_id" name="customer" required>
          <option value="" disabled selected>Choose customer</option>
          <option *ngFor="let c of customers()" [value]="c.id">{{c.name}}</option>
        </select>
        <select aria-label="Product" [(ngModel)]="order.product_id" name="product" required>
          <option value="" disabled selected>Choose product</option>
          <option *ngFor="let p of products()" [value]="p.id">{{p.name}} (stock {{p.stock}})</option>
        </select>
        <input aria-label="Quantity" type="number" min="1" [(ngModel)]="order.quantity" name="quantity" required>
        <button [disabled]="role==='viewer'">Create draft order</button>
      </form>

      <table>
        <tr><th>ID</th><th>Customer</th><th>Items</th><th>Status</th><th>Total</th><th>Actions</th></tr>
        <ng-container *ngFor="let x of rows()">
          <tr>
            <td>#{{x.id}}</td>
            <td>{{x.customer}}</td>
            <td>{{x.items?.length||0}} line(s)</td>
            <td>{{x.status}}</td>
            <td>{{x.total|currency}}</td>
            <td>
              <button *ngIf="x.status==='draft'&&role!=='viewer'" (click)="transition(x,'validated')">Validate</button>
              <button *ngIf="x.status==='validated'&&role!=='viewer'" (click)="transition(x,'closed')">Close</button>
              <button *ngIf="x.status==='draft'&&role!=='viewer'" (click)="remove(x.id)">Delete</button>
              <button (click)="toggleItems(x.id)">{{expandedOrder===x.id?'Hide items':'View items'}}</button>
            </td>
          </tr>
          <tr *ngIf="expandedOrder===x.id">
            <td colspan="6" style="background:#f4f6f8;padding:12px">
              <b>Order #{{x.id}} Items:</b>
              <ul>
                <li *ngFor="let it of x.items">
                  {{it.product}} &times; {{it.quantity}} &#64; {{it.unit_price|currency}}
                  <button *ngIf="x.status==='draft'&&role!=='viewer'&&x.items.length>1" (click)="removeOrderItem(it.id)" style="margin-left:8px">Delete line</button>
                </li>
              </ul>
              <form *ngIf="x.status==='draft'&&role!=='viewer'" (ngSubmit)="addOrderItem(x.id)" style="margin-top:8px;display:flex;gap:6px">
                <select [(ngModel)]="newItem.product_id" name="newProd" required>
                  <option value="" disabled selected>Add product line</option>
                  <option *ngFor="let p of products()" [value]="p.id">{{p.name}} (stock {{p.stock}})</option>
                </select>
                <input type="number" min="1" [(ngModel)]="newItem.quantity" name="newQty" style="width:70px" required>
                <button>Add line</button>
              </form>
            </td>
          </tr>
        </ng-container>
      </table>
    </div>

    <table *ngIf="section==='audit'">
      <tr><th>When</th><th>Actor</th><th>Action</th><th>Entity</th></tr>
      <tr *ngFor="let x of rows()">
        <td>{{x.at}}</td>
        <td>{{x.actor}}</td>
        <td>{{x.action}}</td>
        <td>{{x.entity}} #{{x.entity_id}}</td>
      </tr>
    </table>
  </section>

  <footer>Demo accounts: admin / Admin123! · sales / Sales123! · viewer / View123!</footer>
</main>`,
  styleUrl: './styles.css'
})
class AppComponent {
  constructor(private cdr: ChangeDetectorRef) {}
  api = location.protocol + '//' + location.hostname + ':8000/api';
  username = 'admin';
  password = 'Admin123!';
  token = '';
  role = '';
  section = 'products';
  rows = signal<any[]>([]);
  stats = signal<any>({});
  query = '';
  dashboardStatus = '';
  message = '';
  editing = 0;
  expandedOrder = 0;
  form: any = { name: '', sku: '', price: 1, stock: 0, email: '' };
  order: any = { customer_id: '', product_id: '', quantity: 1 };
  newItem: any = { product_id: '', quantity: 1 };
  customers = signal<any[]>([]);
  products = signal<any[]>([]);

  async req(path: string, opt: any = {}) {
    const r = await fetch(this.api + path, {
      ...opt,
      headers: {
        'Content-Type': 'application/json',
        ...(this.token ? { Authorization: 'Bearer ' + this.token } : {}),
        ...(opt.headers || {})
      }
    });
    if (!r.ok) {
      const e = await r.json().catch(() => ({}));
      throw Error(e.detail || `HTTP ${r.status}`);
    }
    return r.status === 204 ? null : r.json();
  }

  async login() {
    try {
      const r = await fetch(this.api + '/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: this.username, password: this.password })
      });
      if (!r.ok) throw Error('Login failed');
      const x = await r.json();
      this.token = x.access_token;
      this.role = x.role;
      this.message = `Signed in as ${this.username} (${this.role})`;
      await this.refresh();
    } catch (e: any) {
      this.message = e.message;
    }
  }

  async refresh() {
    try {
      this.stats.set(await this.req('/dashboard' + (this.dashboardStatus ? '?status=' + this.dashboardStatus : '')));
      this.cdr.detectChanges();
      await this.load();
    } catch (e: any) {
      this.message = e.message;
    }
  }

  async show(s: string) {
    this.section = s;
    this.query = '';
    this.editing = 0;
    this.expandedOrder = 0;
    if (s === 'orders') {
      try {
        const [cList, pList] = await Promise.all([
          this.req('/customers'),
          this.req('/products')
        ]);
        this.customers.set(cList);
        this.products.set(pList);
        this.cdr.detectChanges();
      } catch (e: any) {
        this.message = e.message;
      }
    }
    await this.load();
  }

  async load() {
    if (!this.token) return;
    try {
      const endpoint = this.section === 'products'
        ? `/products?q=${encodeURIComponent(this.query)}`
        : this.section === 'customers'
        ? `/customers?q=${encodeURIComponent(this.query)}`
        : this.section === 'orders'
        ? '/orders'
        : '/audit';
      this.rows.set(await this.req(endpoint));
      this.cdr.detectChanges();
    } catch (e: any) {
      this.message = e.message;
      this.cdr.detectChanges();
    }
  }

  toggleItems(oid: number) {
    this.expandedOrder = this.expandedOrder === oid ? 0 : oid;
  }

  edit(x: any) {
    this.editing = x.id;
    this.form = { ...x };
  }

  reset() {
    this.editing = 0;
    this.form = { name: '', sku: '', price: 1, stock: 0, email: '' };
  }

  async saveProduct() {
    try {
      await this.req('/products' + (this.editing ? `/${this.editing}` : ''), {
        method: this.editing ? 'PUT' : 'POST',
        body: JSON.stringify({ ...this.form, price: +this.form.price, stock: +this.form.stock })
      });
      this.message = 'Product saved';
      this.reset();
      await this.refresh();
    } catch (e: any) {
      this.message = e.message;
    }
  }

  async saveCustomer() {
    try {
      await this.req('/customers' + (this.editing ? `/${this.editing}` : ''), {
        method: this.editing ? 'PUT' : 'POST',
        body: JSON.stringify({ name: this.form.name, email: this.form.email })
      });
      this.message = 'Customer saved';
      this.reset();
      await this.refresh();
    } catch (e: any) {
      this.message = e.message;
    }
  }

  async createOrder() {
    try {
      if (!this.order.customer_id || !this.order.product_id) {
        this.message = 'Please select a customer and product';
        return;
      }
      const x = await this.req('/orders', {
        method: 'POST',
        body: JSON.stringify({
          customer_id: +this.order.customer_id,
          items: [{ product_id: +this.order.product_id, quantity: +this.order.quantity }]
        })
      });
      this.message = `Draft order #${x.id} created`;
      this.order = { customer_id: '', product_id: '', quantity: 1 };
      await this.refresh();
    } catch (e: any) {
      this.message = e.message;
    }
  }

  async addOrderItem(oid: number) {
    try {
      if (!this.newItem.product_id) return;
      await this.req(`/orders/${oid}/items`, {
        method: 'POST',
        body: JSON.stringify({ product_id: +this.newItem.product_id, quantity: +this.newItem.quantity })
      });
      this.message = `Item added to order #${oid}`;
      this.newItem = { product_id: '', quantity: 1 };
      await this.refresh();
    } catch (e: any) {
      this.message = e.message;
    }
  }

  async removeOrderItem(iid: number) {
    try {
      await this.req(`/order-items/${iid}`, { method: 'DELETE' });
      this.message = 'Item deleted';
      await this.refresh();
    } catch (e: any) {
      this.message = e.message;
    }
  }

  async transition(x: any, status: string) {
    try {
      await this.req(`/orders/${x.id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status })
      });
      this.message = `Order #${x.id} ${status}`;
      await this.refresh();
    } catch (e: any) {
      this.message = e.message;
    }
  }

  async remove(id: number) {
    if (!confirm('Delete this record?')) return;
    try {
      const path = this.section === 'orders' ? `/orders/${id}` : `/${this.section}/${id}`;
      await this.req(path, { method: 'DELETE' });
      this.message = 'Deleted';
      await this.refresh();
    } catch (e: any) {
      this.message = e.message;
    }
  }
}

bootstrapApplication(AppComponent).catch(console.error);

