<template>
  <div>
    <div class="inputs">
      <div v-if="isLoading" class="verifying">
        <b-loading :is-full-page="false" :active="true"></b-loading>
        <p class="loading-text">Verifying your magic link...</p>
      </div>
      <div v-else-if="error" class="error-state">
        <b-icon icon="exclamation-circle" type="is-danger" size="is-large"></b-icon>
        <p class="error-text">{{ error }}</p>
        <b-button
          type="is-primary"
          size="is-medium"
          expanded
          class="mt-20"
          @click="goToMagicLink"
        >
          Request New Link
        </b-button>
        <h1 class="mt-20 alt-button" @click="goToLogin">Back to Login</h1>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useHead } from '@unhead/vue';
import { getCurrentInstance, ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Requests } from '../services/requests';
import { setToken } from '../services/user';

useHead({
  title: 'Signing In...',
});

const router = useRouter();
const route = useRoute();
const instance = getCurrentInstance();
const buefy = (instance?.appContext.config.globalProperties as any).$buefy;

const isLoading = ref(true);
const error = ref('');

const goToLogin = () => {
  router.push({ name: 'Login' });
};

const goToMagicLink = () => {
  router.push({ name: 'Magic Link' });
};

onMounted(async () => {
  const token = (route.query.token as string) || '';

  if (!token) {
    error.value = 'No token provided';
    isLoading.value = false;
    return;
  }

  try {
    const res = await Requests.post('/magic-link/verify', { token });
    if (res.data?.access_token) {
      setToken(res.data.access_token);
      buefy?.toast.open({
        duration: 3000,
        message: 'Successfully signed in!',
        position: 'is-top',
        type: 'is-success',
      });
      router.push({ name: 'Home Redirect' });
    } else {
      throw new Error('Invalid response');
    }
  } catch (e: any) {
    if (e.response?.data?.error) {
      error.value = e.response.data.error;
    } else {
      error.value = 'This link is invalid or has expired.';
    }
  }

  isLoading.value = false;
});
</script>

<style scoped>
.verifying {
  text-align: center;
  padding: 40px 0;
  position: relative;
  min-height: 100px;
}

.loading-text {
  color: var(--text-secondary, #666);
  margin-top: 60px;
  font-size: 14px;
}

.error-state {
  text-align: center;
  padding: 20px 0;
}

.error-text {
  color: var(--text-secondary, #666);
  margin-top: 15px;
  font-size: 14px;
}
</style>
