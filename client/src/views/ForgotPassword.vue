<template>
  <div>
    <div class="msgs">{{ errMsg }}</div>
    <div class="inputs" v-if="!submitted">
      <p class="info-text">Enter your email address and we'll send you a link to reset your password.</p>
      <b-field :type="emailErr ? 'is-danger' : ''" :message="emailErr">
        <b-input
          placeholder="Email"
          type="email"
          size="is-medium"
          icon="envelope"
          v-model="email"
          @keyup.enter="submit"
        ></b-input>
      </b-field>
      <b-button
        type="is-primary"
        size="is-medium"
        expanded
        class="mt-20"
        @click="submit"
        :loading="isLoading"
      >
        Send Reset Link
      </b-button>
      <h1 class="mt-20 alt-button" @click="goToLogin">Back to Login</h1>
    </div>
    <div class="inputs" v-else>
      <div class="success-message">
        <b-icon icon="check-circle" type="is-success" size="is-large"></b-icon>
        <p class="success-text">
          If an account exists with that email, you'll receive a password reset link shortly.
        </p>
      </div>
      <b-button
        type="is-primary"
        size="is-medium"
        expanded
        class="mt-20"
        @click="goToLogin"
      >
        Back to Login
      </b-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useHead } from '@unhead/vue';
import { getCurrentInstance, ref } from 'vue';
import { useRouter } from 'vue-router';
import { Requests } from '../services/requests';

useHead({
  title: 'Forgot Password',
});

const router = useRouter();
const instance = getCurrentInstance();
const buefy = (instance?.appContext.config.globalProperties as any).$buefy;

const email = ref('');
const emailErr = ref('');
const errMsg = ref('');
const isLoading = ref(false);
const submitted = ref(false);

const goToLogin = () => {
  router.push({ name: 'Login' });
};

const submit = async () => {
  if (isLoading.value) {
    return;
  }

  emailErr.value = '';
  errMsg.value = '';

  if (!email.value || !email.value.length) {
    emailErr.value = 'Email is required';
    return;
  }

  if (!email.value.includes('@')) {
    emailErr.value = 'Please enter a valid email address';
    return;
  }

  isLoading.value = true;

  try {
    await Requests.post('/forgot-password', {
      email: email.value,
    });
    submitted.value = true;
  } catch (e: any) {
    if (e.response?.status === 429) {
      errMsg.value = 'Too many requests. Please try again later.';
    } else {
      errMsg.value = 'There was an error. Please try again.';
    }
    buefy?.toast.open({
      duration: 5000,
      message: errMsg.value,
      position: 'is-top',
      type: 'is-danger',
    });
  }

  isLoading.value = false;
};
</script>

<style scoped>
.info-text {
  color: var(--text-secondary, #666);
  margin-bottom: 20px;
  text-align: center;
  font-size: 14px;
}

.success-message {
  text-align: center;
  padding: 20px 0;
}

.success-text {
  color: var(--text-secondary, #666);
  margin-top: 15px;
  font-size: 14px;
}
</style>
