<template>
  <section>
    <div class="row">
      <div class="col-md-6">
        <div class="card shadow mb-4">
          <div class="card-body">
            <div class="form-group">
              <label for="">Product Name</label>
              <input type="text" v-model="product_name" placeholder="Product Name" class="form-control">
            </div>
            <div class="form-group">
              <label for="">Product SKU</label>
              <input type="text" v-model="product_sku" placeholder="Product Name" class="form-control">
            </div>
            <div class="form-group">
              <label for="">Description</label>
              <textarea v-model="description" id="" cols="30" rows="4" class="form-control"></textarea>
            </div>
          </div>
        </div>

        <div class="card shadow mb-4">
          <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
            <h6 class="m-0 font-weight-bold text-primary">Media</h6>
          </div>
          <div class="card-body border">
            <vue-dropzone ref="myVueDropzone" id="dropzone" :options="dropzoneOptions"></vue-dropzone>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card shadow mb-4">
          <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
            <h6 class="m-0 font-weight-bold text-primary">Variants</h6>
          </div>

          <div class="card-body">
            <div class="table-responsive">
              <table class="table">
                <thead>
                <tr>
                  <td>Variant</td>
                  <td>Price</td>
                  <td>Stock</td>
                </tr>
                </thead>
                <tbody>
                <tr v-for="variant_price in product_variant_prices">
                  <td>{{ variant_price.title }}</td>
                  <td>
                    <input type="text" class="form-control" v-model="variant_price.price">
                  </td>
                  <td>
                    <input type="text" class="form-control" v-model="variant_price.stock">
                  </td>
                  <td>
                    <button @click="deleteVariant(variant_price.id)" type="button" class="btn btn-outline-danger">Delete</button>
                  </td>
                </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <button @click="saveProduct" type="submit" class="btn btn-lg btn-primary">Update</button>
    <button type="button" class="btn btn-secondary btn-lg">Cancel</button>
  </section>
</template>

<script>
import vue2Dropzone from 'vue2-dropzone'
import 'vue2-dropzone/dist/vue2Dropzone.min.css'
import InputTag from 'vue-input-tag'
import axios from 'axios'

export default {
  components: {
    vueDropzone: vue2Dropzone,
    InputTag
  },
  props: {
    variants: {
      type: Array,
      required: true
    }
  },
  data() {

    return {
      product_name: '',
      product_sku: '',
      description: '',
      images: [],
      product_variant: [
        {
          option: this.variants[0].id,
          tags: []
        }
      ],
      product_variant_prices: [],
      dropzoneOptions: {
        url: 'https://httpbin.org/post',
        thumbnailWidth: 150,
        maxFilesize: 0.5,
        headers: {"My-Awesome-Header": "header value"}
      }
    }
  },
  methods: {
    // it will push a new object into product variant
    newVariant() {
      let all_variants = this.variants.map(el => el.id)
      let selected_variants = this.product_variant.map(el => el.option);
      let available_variants = all_variants.filter(entry1 => !selected_variants.some(entry2 => entry1 == entry2))
      // console.log(available_variants)

      this.product_variant.push({
        option: available_variants[0],
        tags: []
      })
    },

    // fetch all availabe product variant prices
    getAllProductVariantPrices() {
      const productId = parseInt(JSON.parse(document.getElementById('product_id').textContent));
      const url = `/product/retrieve-product/${productId}/`;
    
      fetch(url)
      .then(response => {
        return response.json();
      })
      .then(data => {
        console.log(data);
        this.product_name = data.title;
        this.product_sku = data.sku;
        this.description = data.description;
        this.product_variant_prices = data.product_variant_prices;
      })
      .catch(error => {
        alert("something went wrong");
      })

    },

    // delete product variant price
    deleteVariant(id) {
      const url = `/product/delete-product-variant-price/${id}/`;
      fetch(url, {
        method: "DELETE",
        headers: {
          "X-CSRFToken": this.getCookie('csrftoken'),
        },
      })
      .then(response => {
        return response.json();
      })
      .then(data => {
        this.getAllProductVariantPrices();
      })
      .catch(e => {
        console.log(e);
      })
    },

    // check the variant and render all the combination
    checkVariant() {
      let tags = [];
      this.product_variant_prices = [];
      this.product_variant.filter((item) => {
        tags.push(item.tags);
      })

      this.getCombn(tags).forEach(item => {
        this.product_variant_prices.push({
          title: item,
          price: 0,
          stock: 0
        })
      })
    },

    // combination algorithm
    getCombn(arr, pre) {
      pre = pre || '';
      if (!arr.length) {
        return pre;
      }
      let self = this;
      let ans = arr[0].reduce(function (ans, value) {
        return ans.concat(self.getCombn(arr.slice(1), pre + value + '/'));
      }, []);
      return ans;
    },

    // get csrf token
     getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    // store product into database
    saveProduct() {
      let product = {
        title: this.product_name,
        sku: this.product_sku,
        description: this.description,
        product_image: this.images,
        product_variant: this.product_variant,
        product_variant_prices: this.product_variant_prices
      }

      const csrftoken = this.getCookie('csrftoken');
      const productId = parseInt(JSON.parse(document.getElementById('product_id').textContent));
      let url = `/product/edit-product/${productId}/`;
      
      fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify(product)
      })
      .then(response => {
        return response.json();
      })
      .then(data => {
        if(data.success) {
          window.location.reload();
        }
        else {
          alert(JSON.stringify(data));
        }
      })
      .catch(error => {
        console.log(error);
      })

      console.log(product);
    }


  },
  mounted() {
    this.getAllProductVariantPrices();
    console.log('Component mounted.')
  }
}
</script>