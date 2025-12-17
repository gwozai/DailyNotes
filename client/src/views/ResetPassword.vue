<template>
  <div>
    <div class="msgs">{{ errMsg }}</div>
    <div class="inputs" v-if="!success">
      <p class="info-text">Enter your new password below.</p>
      <b-field :type="passwordErr ? 'is-danger' : ''" :message="passwordErr">
        <b-input
          placeholder="New Password"
          type="password"
          password-reveal
          size="is-medium"
          icon="key"
          v-model="password"
          @keyup.enter="submit"
        ></b-input>
      </b-field>
      <b-field :type="confirmErr ? 'is-danger' : ''" :message="confirmErr">
        <b-input
          placeholder="Confirm Password"
          type="password"
          password-reveal
          size="is-medium"
          icon="key"
          v-model="confirmPassword"
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
        Reset Password
      </b-button>
    </div>
    <div class="inputs" v-else>
      <div class="success-message">
        <b-icon icon="check-circle" type="is-success" size="is-large"></b-icon>
        <p class="success-text">Your password has been reset successfully!</p>
      </div>
      <b-button
        type="is-primary"
        size="is-medium"
        expanded
        class="mt-20"
        @click="goToLogin"
      >
        Continue to Login
      </b-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useHead } from '@unhead/vue';
import { getCurrentInstance, ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Requests } from '../services/requests';

useHead({
  title: 'Reset Password',
});

const router = useRouter();
const route = useRoute();
const instance = getCurrentInstance();
const buefy = (instance?.appContext.config.globalProperties as any).$buefy;

const password = ref('');
const passwordErr = ref('');
const confirmPassword = ref('');
const confirmErr = ref('');
const errMsg = ref('');
const isLoading = ref(false);
const success = ref(false);
const token = ref('');

onMounted(() => {
  token.value = (route.query.token as string) || '';
  if (!token.value) {
    errMsg.value = 'Invalid or missing reset token';
  }
});

const goToLogin = () => {
  router.push({ name: 'Login' });
};

const submit = async () => {
  if (isLoading.value) {
    return;
  }

  passwordErr.value = '';
  confirmErr.value = '';
  errMsg.value = '';

  if (!password.value || !password.value.length) {
    passwordErr.value = 'Password is required';
    return;
  }

  if (password.value.length < 4) {
    passwordErr.value = 'Password must be at least 4 characters';
    return;
  }

  if (password.value !== confirmPassword.value) {
    confirmErr.value = 'Passwords do not match';
    return;
  }

  if (!token.value) {
    errMsg.value = 'Invalid or missing reset token';
    return;
  }

  isLoading.value = true;

  try {
    await Requests.post('/reset-password', {
      token: token.value,
      password: password.value,
    });
    success.value = true;
    buefy?.toast.open({
      duration: 5000,
      message: 'Password reset successfully!',
      position: 'is-top',
      type: 'is-success',
    });
  } catch (e: any) {
    if (e.response?.data?.error) {
      errMsg.value = e.response.data.error;
    } else {
      errMsg.value = 'Invalid or expired reset link. Please request a new one.';
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
