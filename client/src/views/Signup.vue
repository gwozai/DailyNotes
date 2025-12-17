<template>
  <div>
    <div class="msgs">{{ errMsg }}</div>
    <div class="inputs">
      <b-field :type="usernameErr ? 'is-danger' : ''" :message="usernameErr">
        <b-input
          placeholder="Username"
          size="is-medium"
          icon="user"
          v-model="username"
          @keyup.enter="signup"
        ></b-input>
      </b-field>
      <b-field :type="emailErr ? 'is-danger' : ''" :message="emailErr">
        <b-input
          placeholder="Email (optional)"
          type="email"
          size="is-medium"
          icon="envelope"
          v-model="email"
          @keyup.enter="signup"
        ></b-input>
      </b-field>
      <p class="email-hint">Add email to enable password recovery and magic link sign-in</p>
      <b-field :type="passwordErr ? 'is-danger' : ''" :message="passwordErr">
        <b-input
          placeholder="Password"
          type="password"
          password-reveal
          size="is-medium"
          icon="key"
          v-model="password"
          @keyup.enter="signup"
        ></b-input>
      </b-field>
      <b-field :type="passConfirmErr ? 'is-danger' : ''" :message="passConfirmErr">
        <b-input
          placeholder="Confirm Password"
          type="password"
          password-reveal
          size="is-medium"
          icon="key"
          v-model="passwordConfirm"
          @keyup.enter="signup"
        ></b-input>
      </b-field>
      <b-button
        type="is-primary"
        size="is-medium"
        expanded
        class="mt-20"
        @click="signup"
        :loading="isLoading"
      >
        Sign Up
      </b-button>
      <h1 class="mt-20 alt-button" @click="login">Login</h1>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useHead } from '@unhead/vue';
import { getCurrentInstance, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Requests } from '../services/requests';
import { setToken } from '../services/user';

useHead({
  title: 'Sign Up',
});

const router = useRouter();
const route = useRoute();
const instance = getCurrentInstance();
const buefy = (instance?.appContext.config.globalProperties as any).$buefy;

const username = ref('');
const usernameErr = ref('');
const email = ref('');
const emailErr = ref('');
const password = ref('');
const passwordErr = ref('');
const passwordConfirm = ref('');
const passConfirmErr = ref('');
const errMsg = ref('');
const isLoading = ref(false);
const hideSignup = !!process.env.VUE_APP_PREVENT_SIGNUPS;

onMounted(() => {
  if (hideSignup) {
    router.push({ name: 'Login' });
  }
});

const login = () => {
  router.push({ name: 'Login' });
};

const signup = async () => {
  if (isLoading.value) {
    return;
  }

  usernameErr.value = '';
  emailErr.value = '';
  passwordErr.value = '';
  passConfirmErr.value = '';
  errMsg.value = '';

  if (!username.value || !username.value.length) {
    usernameErr.value = 'Username must be filled';
    return;
  }

  // Validate email format if provided
  if (email.value && email.value.length > 0) {
    if (!email.value.includes('@') || !email.value.includes('.')) {
      emailErr.value = 'Please enter a valid email address';
      return;
    }
  }

  if (!password.value || !password.value.length) {
    passwordErr.value = 'Password must be filled.';
    return;
  }

  if (password.value !== passwordConfirm.value) {
    passConfirmErr.value = 'Passwords must match.';
    return;
  }

  isLoading.value = true;

  try {
    const payload: { username: string; password: string; email?: string } = {
      username: username.value,
      password: password.value,
    };

    // Only include email if provided
    if (email.value && email.value.trim().length > 0) {
      payload.email = email.value.trim();
    }

    const res = await Requests.post('/sign-up', payload);
    if (res.data?.access_token) {
      setToken(res.data.access_token);

      if (route.query?.from) {
        router.push({ path: String(route.query.from) });
      } else {
        router.push({ name: 'Home Redirect' });
      }
    } else {
      throw Error("Data isn't right");
    }
  } catch (e) {
    console.log(e);

    errMsg.value = 'There was an error creating your account. Please try again.';
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
.email-hint {
  color: var(--text-muted, #999);
  font-size: 12px;
  margin: -8px 0 12px 0;
  text-align: center;
}
</style>
